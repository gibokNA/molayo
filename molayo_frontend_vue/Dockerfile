FROM nginx:latest

COPY ./dist /usr/share/nginx/html

RUN mkdir /usr/share/nginx/html/static

COPY ./default.conf /etc/nginx/conf.d/default.conf