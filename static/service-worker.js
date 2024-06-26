
  self.addEventListener('install', (event) => {
    console.log('Service worker installing...');

    event.waitUntil(
      caches.open('v1').then((cache) => {
        return cache.addAll([
          
          '/static/styles.css',
          '/static/script.js',
          '/static/RO.svg',
          '../templates/index.html',
        ]);
      })
    );
  });
  



  self.addEventListener('fetch', function(event) {
    event.respondWith(
      caches.match(event.request).then(function(response) {
  
        return response || fetch(event.request);
      })
    );
  });

   

  self.addEventListener('push', event => {
    console.log('Push notification received', event);

  });
  

  