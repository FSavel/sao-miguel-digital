const CACHE_NAME = 'paroquia-sao-miguel-cache-v1';

// Arquivos e rotas essenciais que serão baixados logo no primeiro acesso
const ASSETS_TO_CACHE = [
  '/',
  '/static/style.css',
  '/static/manifest.json',
  '/avisos',
  '/leituras',
  '/canticos',
  '/escalas',
  '/calendario'
];

// 1. Evento de Instalação: Salva as páginas principais na memória do celular
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Armazenando páginas essenciais para uso offline...');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => self.skipWaiting()) // Força o Service Worker a ativar imediatamente
  );
});

// 2. Evento de Ativação: Limpa caches antigos se você atualizar o aplicativo no futuro
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('Removendo cache antigo:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 3. Evento Fetch: Gerencia os pedidos de páginas quando o usuário navega
self.addEventListener('fetch', (event) => {
  // Ignora requisições de métodos de envio (como formulários POST de administração)
  if (event.request.method !== 'GET') return;

  event.respondWith(
    // Tenta buscar a versão mais recente pela internet
    fetch(event.request)
      .then((networkResponse) => {
        // Se encontrar internet, guarda uma cópia atualizada no cache e mostra ao usuário
        if (networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // SE DER ERRO (Sem Internet): Busca imediatamente a cópia salva na memória do celular
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          // Se nem a página estiver no cache e estiver sem rede, retorna erro básico
          return new Response('Conteúdo indisponível offline.', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({ 'Content-Type': 'text/plain; charset=utf-8' })
          });
        });
      })
  );
});