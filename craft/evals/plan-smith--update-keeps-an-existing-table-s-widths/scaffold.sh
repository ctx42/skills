#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/tenancy

go 1.22
EOF_0
mkdir -p tmp
cat > tmp/wide-column-plan.md <<'EOF_1'
# Tenant isolation plan

## Summary

| #  | Item                         | Status |
|----|------------------------------|--------|
| 1  | Row-level filters            | N      |
| 2  | Per-tenant keys              | N      |
| 3  | Cross-tenant tests           | N      |

Legend: Y implemented · N not yet · X rejected

## 1. Row-level filters — [ ]

Every query against a tenant-scoped table carries the tenant id, applied by the
repository layer rather than by each call site.

Done when: a query built without a tenant id fails to compile, and the
integration suite covers one table per repository.

## 2. Per-tenant keys — [ ]

Encryption keys are derived per tenant so one tenant's leaked key cannot open
another's data.

Done when: key derivation takes the tenant id, and rotating one tenant's key
leaves the others readable.

## 3. Cross-tenant tests — [ ]

A suite that asserts tenant A cannot read, write, or enumerate tenant B.

Done when: the suite exists and fails if the row-level filter is removed.
EOF_1
mkdir -p store
cat > store/query.go <<'EOF_2'
// Package store is the repository layer; every query it runs is scoped to
// one tenant.
package store

import "strconv"

// TenantID identifies a tenant.
type TenantID string

// Cond is one extra WHERE condition with its argument.
type Cond struct {
	Expr string // e.g. "status = ?"
	Arg  any
}

// scoped renders a SELECT on table for tenant t. The tenant filter is always
// the first condition; repositories are the only callers, and each takes the
// tenant as a required parameter, so a query without a tenant id does not
// compile.
func scoped(table string, t TenantID, where []Cond) (string, []any) {
	sql := "SELECT * FROM " + table + " WHERE tenant_id = $1"
	args := []any{string(t)}
	for i, c := range where {
		sql += " AND " + c.Expr + " $" + strconv.Itoa(i+2)
		args = append(args, c.Arg)
	}
	return sql, args
}
EOF_2
mkdir -p store
cat > store/users.go <<'EOF_3'
package store

import (
	"context"
	"database/sql"
)

// Users is the repository for the users table.
type Users struct{ db *sql.DB }

// List returns tenant t's users matching where.
func (r Users) List(ctx context.Context, t TenantID, where ...Cond) (*sql.Rows, error) {
	q, args := scoped("users", t, where)
	return r.db.QueryContext(ctx, q, args...)
}
EOF_3
mkdir -p store
cat > store/invoices.go <<'EOF_4'
package store

import (
	"context"
	"database/sql"
)

// Invoices is the repository for the invoices table.
type Invoices struct{ db *sql.DB }

// List returns tenant t's invoices matching where.
func (r Invoices) List(ctx context.Context, t TenantID, where ...Cond) (*sql.Rows, error) {
	q, args := scoped("invoices", t, where)
	return r.db.QueryContext(ctx, q, args...)
}
EOF_4
mkdir -p store
cat > store/users_integration_test.go <<'EOF_5'
//go:build integration

package store

import (
	"context"
	"testing"
)

func Test_Users_List_ScopesToTenant(t *testing.T) {
	db := openTestDB(t)
	seed(t, db, "users", "acme", "globex")
	rows, err := Users{db: db}.List(context.Background(), "acme")
	if err != nil {
		t.Fatal(err)
	}
	assertOnlyTenant(t, rows, "acme")
}
EOF_5
mkdir -p store
cat > store/invoices_integration_test.go <<'EOF_6'
//go:build integration

package store

import (
	"context"
	"testing"
)

func Test_Invoices_List_ScopesToTenant(t *testing.T) {
	db := openTestDB(t)
	seed(t, db, "invoices", "acme", "globex")
	rows, err := Invoices{db: db}.List(context.Background(), "acme")
	if err != nil {
		t.Fatal(err)
	}
	assertOnlyTenant(t, rows, "acme")
}
EOF_6
mkdir -p store
cat > store/helpers_integration_test.go <<'EOF_7'
//go:build integration

package store

import (
	"database/sql"
	"os"
	"testing"

	_ "github.com/jackc/pgx/v5/stdlib"
)

func openTestDB(t *testing.T) *sql.DB {
	t.Helper()
	db, err := sql.Open("pgx", os.Getenv("TEST_DATABASE_URL"))
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = db.Close() })
	return db
}

func seed(t *testing.T, db *sql.DB, table string, tenants ...string) {
	t.Helper()
	for _, tn := range tenants {
		if _, err := db.Exec("INSERT INTO "+table+" (tenant_id) VALUES ($1)", tn); err != nil {
			t.Fatal(err)
		}
	}
}

func assertOnlyTenant(t *testing.T, rows *sql.Rows, want string) {
	t.Helper()
	defer rows.Close()
	cols, _ := rows.Columns()
	for rows.Next() {
		vals := make([]any, len(cols))
		ptrs := make([]any, len(cols))
		for i := range vals {
			ptrs[i] = &vals[i]
		}
		_ = rows.Scan(ptrs...)
		for i, c := range cols {
			if c == "tenant_id" && vals[i] != want {
				t.Fatalf("want only tenant %s, have %v", want, vals[i])
			}
		}
	}
}
EOF_7
mkdir -p api
cat > api/export.go <<'EOF_8'
// Package api serves the tenant-facing HTTP API.
package api

import "net/http"

// TODO: per-tenant quotas — cap requests per tenant per minute so one
// tenant cannot starve the others.

// Export streams a tenant's data export.
func Export(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusNotImplemented)
}
EOF_8
