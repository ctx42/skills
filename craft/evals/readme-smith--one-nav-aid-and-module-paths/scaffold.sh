#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module bitbucket.org/acme/foo

go 1.22
EOF_0
mkdir -p pkg/foo
cat > pkg/foo/queue.go <<'EOF_1'
// Package foo is an in-process job queue with bounded capacity, retries with
// backoff, and drain-on-shutdown.
package foo

import (
	"context"
	"errors"
	"sync"
	"time"
)

// ErrFull is returned by Push when the queue is at capacity.
var ErrFull = errors.New("foo: queue full")

// ErrClosed is returned by Push after Drain has been called.
var ErrClosed = errors.New("foo: queue closed")

// Job is a unit of work. A Job that returns an error is retried.
type Job func(ctx context.Context) error

// Option configures a Queue.
type Option func(*Queue)

// WithCapacity bounds how many jobs may wait; the default is 128.
func WithCapacity(n int) Option { return func(q *Queue) { q.capacity = n } }

// WithWorkers sets how many jobs run at once; the default is 4.
func WithWorkers(n int) Option { return func(q *Queue) { q.workers = n } }

// WithRetry sets the attempts per job and the base backoff, doubled after each
// failure; the default is 3 attempts from 100ms.
func WithRetry(attempts int, base time.Duration) Option {
	return func(q *Queue) { q.attempts, q.backoff = attempts, base }
}

// Stats reports queue counters.
type Stats struct {
	Pending   int
	Succeeded int
	Failed    int
	Retried   int
}

// Queue runs Jobs on a fixed pool of workers.
type Queue struct {
	capacity, workers, attempts int
	backoff                     time.Duration

	mu     sync.Mutex
	jobs   chan Job
	closed bool
	stats  Stats
	wg     sync.WaitGroup
}

// New starts a Queue with its workers running.
func New(opts ...Option) *Queue {
	q := &Queue{capacity: 128, workers: 4, attempts: 3, backoff: 100 * time.Millisecond}
	for _, o := range opts {
		o(q)
	}
	q.jobs = make(chan Job, q.capacity)
	for i := 0; i < q.workers; i++ {
		q.wg.Add(1)
		go q.work()
	}
	return q
}

// Push enqueues job without blocking.
func (q *Queue) Push(job Job) error {
	q.mu.Lock()
	defer q.mu.Unlock()
	if q.closed {
		return ErrClosed
	}
	select {
	case q.jobs <- job:
		q.stats.Pending++
		return nil
	default:
		return ErrFull
	}
}

// Stats returns a snapshot of the counters.
func (q *Queue) Stats() Stats {
	q.mu.Lock()
	defer q.mu.Unlock()
	return q.stats
}

// Drain stops accepting jobs and waits until queued jobs finish or ctx ends.
func (q *Queue) Drain(ctx context.Context) error {
	q.mu.Lock()
	if !q.closed {
		q.closed = true
		close(q.jobs)
	}
	q.mu.Unlock()
	done := make(chan struct{})
	go func() { q.wg.Wait(); close(done) }()
	select {
	case <-done:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func (q *Queue) work() {
	defer q.wg.Done()
	for job := range q.jobs {
		q.run(job)
	}
}

func (q *Queue) run(job Job) {
	wait := q.backoff
	for i := 0; i < q.attempts; i++ {
		if err := job(context.Background()); err == nil {
			q.count(func(s *Stats) { s.Pending--; s.Succeeded++ })
			return
		}
		if i < q.attempts-1 {
			q.count(func(s *Stats) { s.Retried++ })
			time.Sleep(wait)
			wait *= 2
		}
	}
	q.count(func(s *Stats) { s.Pending--; s.Failed++ })
}

func (q *Queue) count(f func(*Stats)) {
	q.mu.Lock()
	f(&q.stats)
	q.mu.Unlock()
}
EOF_1
mkdir -p pkg/foo
cat > pkg/foo/queue_test.go <<'EOF_2'
package foo

import (
	"context"
	"testing"
)

func TestQueueRunsJob(t *testing.T) {
	q := New(WithWorkers(1))
	ran := make(chan struct{})
	if err := q.Push(func(context.Context) error { close(ran); return nil }); err != nil {
		t.Fatal(err)
	}
	<-ran
	if err := q.Drain(context.Background()); err != nil {
		t.Fatal(err)
	}
}
EOF_2
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
git remote add origin git@bitbucket.org:acme/foo.git
git add -A
git commit -q -m 'chore: initial import'
