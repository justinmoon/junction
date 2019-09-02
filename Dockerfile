FROM electronuserland/builder:wine

# had to downgrade node b/c eslint complaining
# installed as usr/bin/node
# bad node is usr/local/bin/node
# couldn't remove old one
# export PATH=/usr/bin:$PATH fixed it
RUN curl -sL https://deb.nodesource.com/setup_10.x  | bash -
RUN apt-get -y install nodejs
