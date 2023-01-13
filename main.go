package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"remote-file-transporter/api"
)

func main() {
	r := gin.Default()
	r.GET("/download", api.DownloadCallback)
	r.GET("/get_user_dir", api.GetUserDirCallback)
	err := r.Run(":50422")
	if err != nil {
		fmt.Printf("Err:%v\n", err)
		return
	}
}
