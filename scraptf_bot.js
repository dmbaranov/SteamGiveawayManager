const io = require('socket.io-client');

// TODO: Don't forget to add EnterRafle method
const USER_ID = parseInt(process.argv[2]);
const GROUP_ID = parseInt(process.argv[3]);
const HASH = process.argv[4].replace(/['"]+/g, '');
const RAFFLE_ID = process.argv[5];

const Socket = {
  socket: null,
  connecting: false,
  raffleId: null,
  changed: false,
  raffleClosed: false,
  connect: () => {
    if (!Socket.socket && !Socket.connecting) {
      Socket.socket = io('https://ws.scrap.tf', {
        secure: true,
        timeout: 30000,
        reconnectionDelay: 5000,
        reconnectionDelayMax: 10000,
        transports: ['websocket']
      });

      Socket.socket.on('connect', () => {
        console.log("[WS] Connected");
        Socket.doAuth();
      });

      Socket.socket.on('connect_error', (err) => {
          console.log('[WS] Connection error. Falling back to API for queue.');
          console.error(err);
      });

      Socket.socket.on('connect_timeout', () => {
        console.log('[WS] Connection timeout');
      });

      Socket.socket.on('reconnect', (num) => {
        console.log('[WS] Reconnected: ' + num);
        Socket.doAuth();
      });

      Socket.socket.on('reconnecting', () => {
        console.log('[WS] Reconnecting...');
      });

      Socket.socket.on('reconnect_error', (err) => {
        console.log('[WS] Reconnection error.');
        console.error(err);
      });

      Socket.socket.on('reconnect_failed', (err) => {
        console.log('[WS] Couldn\'t connect within max attempts');
        console.error(err);
      });

      Socket.socket.on('auth-response', (data) => {
        Socket.socket.emit('auth-response-response', 'confirm complete connection');
        console.log('[WS] Auth response', data);

        if (!Socket.raffleId && !Socket.raffleClosed) {
          Socket.socket.emit('set-raffle', RAFFLE_ID);
          console.log('[WS] Set raffle');
        }
      });
    }
  },
  doAuth: () => {
    if (!Socket.socket || !Socket.socket.connected) {
      return ;
    }

    console.log('[WS] Doing Auth...');
    Socket.socket.emit('authenticate', {
        "userid": USER_ID,
        "groupid": GROUP_ID,
        "hash": HASH
    });
  }
};

Socket.connect();
