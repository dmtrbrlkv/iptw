# ip2w
IP to weather daemon

The daemon returns the weather in json format in the city determined by the transmitted addresss

### Installation

    yum install ip2w-0.0.1-1.noarch.rpm
    
    
### nginx config
    ...
    server {
        listen 80;
        server_name localhost;

        location /ip2w/ {
            include uwsgi_params;
            uwsgi_pass unix:/run/uwsgi/ip2w.sock;
        }
    }
    ...
