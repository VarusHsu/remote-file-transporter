package main

import (
	"Remote-File_Transporter/api"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.GET("/download", api.DownloadCallback)
	r.GET("/get_user_dir", api.GetUserDirCallback)
	r.Run()
}
