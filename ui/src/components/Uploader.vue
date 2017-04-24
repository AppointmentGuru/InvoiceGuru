<template>
<el-upload
  drag
  class="avatar-uploader"
  action="https://jsonplaceholder.typicode.com/posts/"
  :show-file-list="false"
  :on-success="handleAvatarSuccess"
  :before-upload="beforeAvatarUpload">
  <img v-if="imageUrl" :src="imageUrl" class="avatar">
  <span v-else-if='uploading' class='placeholder' >
    <i class="el-icon-loading avatar-uploader-icon"></i>
    Uploading
  </span>
  <span v-else class='placeholder' >
    <i class="el-icon-plus avatar-uploader-icon"></i>
    Logo
  </span>
</el-upload>
</template>
<style>
  .avatar-uploader .el-upload {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }
  .avatar-uploader .el-upload:hover {
    border-color: #20a0ff;
  }
  .avatar-uploader .el-upload-dragger,
  .avatar {
    width: 178px;
    height: 178px;
    display: block;
  }
  .placeholder {
    line-height: 178px;
    font-size: 28px;
    color: #8c939d;
    width: 178px;
    height: 178px;
    line-height: 178px;
    text-align: center;
    text-transform: uppercase;
  }
</style>

<script>
export default {
  data () {
    return {
      imageUrl: '',
      uploading: false
    }
  },
  methods: {
    handleAvatarSuccess (res, file) {
      this.imageUrl = URL.createObjectURL(file.raw)
      this.uploading = false
    },
    beforeAvatarUpload (file) {
      const isJPG = (file.type === 'image/jpeg' ||
                     file.type === 'image/png')
      const isLt2M = file.size / 100 / 100 < 2

      if (!isJPG) {
        this.$message.error('Logo must be either jpg or png')
      }
      if (!isLt2M) {
        this.$message.error('You logo should be a square, exactly 100x100 pixels')
      }
      let result = (isJPG && isLt2M)
      if (result) { this.uploading = true }
      return result
    }
  }
}
</script>
