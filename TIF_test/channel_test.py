from PIL import Image

# 打开 TIF 文件
image = Image.open("./TIF_test/your_image.tif")

# 获取图像的通道数
channels = image.getbands()

# 打印通道数
print("TIF 文件的通道数为:", len(channels))
print("通道信息:", channels)
