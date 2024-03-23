
  self.addEventListener('install', (event) => {
    console.log('Service worker installing...');
    // Cache list of essential files
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
        // Return the cached response if found, otherwise fetch from the network
        return response || fetch(event.request);
      })
    );
  });

   
   // push notifications to be implemented
  self.addEventListener('push', event => {
    console.log('Push notification received', event);
    // Display a notification here
  });
  

  