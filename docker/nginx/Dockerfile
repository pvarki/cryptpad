ARG NGINX_IMAGE=nginx:1.30.6-alpine@sha256:47928bf67eb62a1863cb08d9ecb52d3e704304ba614eaee17884204677702951

FROM ${NGINX_IMAGE}

RUN apk add --no-cache openssl

COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/nginx/docker-entrypoint.sh /usr/local/bin/nginx-entrypoint.sh
COPY docker/scripts/generate-local-cert.sh /usr/local/bin/generate-local-cert.sh

RUN chmod 0755 /usr/local/bin/nginx-entrypoint.sh /usr/local/bin/generate-local-cert.sh

ENTRYPOINT ["/usr/local/bin/nginx-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
