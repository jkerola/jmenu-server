from alpine:latest
run apk upgrade
run apk add python3 py3-pip
workdir jmenu-server
copy . .
run pip install -r requirements.txt --break-system-packages
expose 5000
entrypoint ["waitress-serve", "app:app"]