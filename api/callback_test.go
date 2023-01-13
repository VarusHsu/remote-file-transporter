package api

import "testing"

func TestWalkDir(t *testing.T) {
	res, err := walkDir("/Users/varus-workstation/GolandProjects")
	if err != nil {
		t.Error(err)
	}
	t.Log(res)
}
