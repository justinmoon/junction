# Clone bitcoind if it doesn't exist, or update it if it does
# (copied from HWI)
cd test
bitcoind_setup_needed=false
if [ ! -d "./bitcoin/.git" ]; then
    echo "    --> cloning bitcoin"
    git clone https://github.com/bitcoin/bitcoin.git
    cd bitcoin
    bitcoind_setup_needed=true
else
    cd bitcoin
    echo "    --> fetching bitcoin"
    git fetch
fi

# Determine if we need to pull. From https://stackoverflow.com/a/3278427
UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
if [ -f ../bitcoin_pin ]; then
    PINNED=$(cat ../bitcoin_pin)
fi
if [ -z PINNED ]; then
    REMOTE=$(git rev-parse "$UPSTREAM")
    BASE=$(git merge-base @ "$UPSTREAM")
    if [ $LOCAL = $REMOTE ]; then
        echo "Up-to-date"
    elif [ $LOCAL = $BASE ]; then
        git pull
        bitcoind_setup_needed=true
    fi
else
    if [ $LOCAL = $PINNED ]; then
        echo "    --> Pinned: $PINNED! Checkout not needed!"
    else
        echo "    --> Pinned: $PINNED! Checkout needed!"
        git pull
        git checkout $PINNED
        bitcoind_setup_needed=true
    fi
fi


# Build bitcoind. This is super slow, but it is cached so it runs fairly quickly.
if [ "$bitcoind_setup_needed" = "true" ] ; then
    ./autogen.sh
    ./configure --with-miniupnpc=no --without-gui --disable-zmq --disable-tests --disable-bench --with-libs=no --with-utils=no
fi
make -j$(nproc) src/bitcoind
cd ../.. #travis is sourcing this script
echo "    --> Finished build bitcoind"

