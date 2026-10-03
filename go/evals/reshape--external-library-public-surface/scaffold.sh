#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/svc

go 1.22

require gopkg.in/yaml.v3 v3.0.1
EOF_0
cat > go.sum <<'EOF_1'
gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405 h1:yhCVgyC4o1eVCa2tZl7eS0r+SDo693bJlVdllGtEeKM=
gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=
gopkg.in/yaml.v3 v3.0.1/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
EOF_1
mkdir -p internal/conf
cat > internal/conf/keys.go <<'EOF_2'
// Package conf reads layered YAML configuration.
package conf

import (
	"fmt"

	"gopkg.in/yaml.v3"
)

// root parses data and returns its top-level mapping node.
func root(data []byte) (*yaml.Node, error) {
	var doc yaml.Node
	if err := yaml.Unmarshal(data, &doc); err != nil {
		return nil, err
	}
	if doc.Kind != yaml.DocumentNode || len(doc.Content) == 0 {
		return nil, fmt.Errorf("empty document")
	}
	top := doc.Content[0]
	if top.Kind != yaml.MappingNode {
		return nil, fmt.Errorf("top level is not a mapping")
	}
	return top, nil
}

// Keys returns the top-level keys of data in document order.
func Keys(data []byte) ([]string, error) {
	top, err := root(data)
	if err != nil {
		return nil, err
	}
	var keys []string
	for i := 0; i+1 < len(top.Content); i += 2 {
		keys = append(keys, top.Content[i].Value)
	}
	return keys, nil
}

// Get returns the scalar value under the top-level key.
func Get(data []byte, key string) (string, bool, error) {
	top, err := root(data)
	if err != nil {
		return "", false, err
	}
	for i := 0; i+1 < len(top.Content); i += 2 {
		if top.Content[i].Value == key {
			return top.Content[i+1].Value, true, nil
		}
	}
	return "", false, nil
}
EOF_2
mkdir -p internal/conf
cat > internal/conf/merge.go <<'EOF_3'
package conf

import (
	"strings"

	"gopkg.in/yaml.v3"
)

// Comments returns the head comment of every top-level key.
func Comments(data []byte) (map[string]string, error) {
	top, err := root(data)
	if err != nil {
		return nil, err
	}
	out := map[string]string{}
	for i := 0; i+1 < len(top.Content); i += 2 {
		k := top.Content[i]
		out[k.Value] = strings.TrimSpace(strings.TrimPrefix(k.HeadComment, "#"))
	}
	return out, nil
}

// Decode decodes data into v, reporting type mismatches as invalid input.
func Decode(data []byte, v any) error {
	err := yaml.Unmarshal(data, v)
	if err != nil && strings.Contains(err.Error(), "cannot unmarshal") {
		return &InvalidError{Msg: err.Error()}
	}
	return err
}

// InvalidError reports YAML whose shape does not match the target.
type InvalidError struct {
	Msg string // Parser message.
}

// Error implements error.
func (e *InvalidError) Error() string { return "invalid config: " + e.Msg }

// Set replaces the scalar under the top-level key and returns the new YAML.
func Set(data []byte, key, value string) ([]byte, error) {
	top, err := root(data)
	if err != nil {
		return nil, err
	}
	for i := 0; i+1 < len(top.Content); i += 2 {
		if top.Content[i].Value == key {
			top.Content[i+1].Value = value
		}
	}
	return yaml.Marshal(top)
}
EOF_3
