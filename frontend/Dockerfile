# 前端 Dockerfile - 开发模式
FROM node:20-alpine

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 暴露端口（Vite开发服务器）
EXPOSE 5173

# 开发模式：使用vite dev server实现热重载
# 源代码通过volume挂载，不需要COPY
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
