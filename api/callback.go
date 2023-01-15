package api

import (
	"encoding/json"
	"github.com/gin-gonic/gin"
	"net/http"
	"os"
	"os/user"
)

const fileItemTypeDir = "dir"
const fileItemTypeFile = "file"

type dir struct {
	DirName string     `json:"dir_name"`
	Items   []fileItem `json:"items"`
}

type fileItem struct {
	Name string `json:"name"`
	Type string `json:"type"`
}

func DownloadCallback(c *gin.Context) {
	path := c.Query("path")
	if path == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"response": "Bad request",
		})
		return
	}
	status, err := os.Stat(path)
	if err != nil {
		if !os.IsExist(err) {
			c.JSON(http.StatusNotFound, gin.H{
				"response": "File or dir don't exist",
			})
			return
		}
	}
	if status.IsDir() {
		items, err := walkDir(path)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{
				"response": "File or dir don't exist",
			})
			return
		} else {
			walkRes := dir{
				DirName: path,
				Items:   items,
			}
			response, err := json.Marshal(walkRes)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{
					"response": "Server error",
				})
				return
			} else {
				c.JSON(http.StatusOK, gin.H{
					"response": string(response),
				})
				return
			}
		}
	} else {
		c.File(path)
	}

}

func GetUserDirCallback(c *gin.Context) {
	u, err := user.Current()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"response": "Server error",
		})
		return
	} else {
		c.JSON(http.StatusOK, gin.H{
			"response": u.HomeDir,
		})
		return
	}
}

func walkDir(root string) ([]fileItem, error) {
	items := make([]fileItem, 0)
	files, err := os.ReadDir(root)
	if err != nil {
		return nil, err
	}
	for _, file := range files {
		fileType := ""
		if file.IsDir() {
			fileType = fileItemTypeDir
		} else {
			fileType = fileItemTypeFile
		}
		item := fileItem{
			Name: file.Name(),
			Type: fileType,
		}
		items = append(items, item)
	}
	return items, nil
}
