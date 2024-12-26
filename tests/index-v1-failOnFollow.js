const express = require('express');
const { IgApiClient } = require('instagram-private-api');
const multer = require('multer');
const axios = require('axios');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const cron = require('node-cron');

const app = express();
const port = 3000;

// Configuração do Multer para upload de imagens
const upload = multer({ storage: multer.memoryStorage() });

// Inicializa o cliente do Instagram
const ig = new IgApiClient();

// Função para salvar a sessão
async function saveSession() {
  const state = await ig.state.serialize();
  delete state.constants; // Remove informações desnecessárias
  fs.writeFileSync('./session.json', JSON.stringify(state));
  console.log('Sessão salva com sucesso.');
}

// Função para restaurar a sessão
async function restoreSession() {
  if (fs.existsSync('./session.json')) {
    const savedState = JSON.parse(fs.readFileSync('./session.json'));
    await ig.state.deserialize(savedState);
    console.log('Sessão restaurada com sucesso.');
  } else {
    console.log('Nenhuma sessão encontrada. Login será necessário.');
  }
}

// Login ou restauração de sessão
(async () => {
  ig.state.generateDevice('dr.economicomics');
  try {
    await restoreSession();
  } catch (error) {
    console.log('Erro ao restaurar a sessão:', error.message);
    console.log('Realizando login manual...');
    await ig.account.login('dr.economicomics', 'PadraoSS2024!');
    await saveSession();
  }
})();

// Função para obter a cor dominante de uma imagem
const getDominantColor = async (buffer) => {
  const { dominant } = await sharp(buffer).stats(); // Pega a cor dominante
  return dominant;
};

// Função para baixar e processar uma imagem
const downloadImage = async (url) => {
  const response = await axios.get(url, { responseType: 'arraybuffer' });
  const buffer = Buffer.from(response.data, 'binary');

  // Pega a cor dominante
  const dominantColor = await getDominantColor(buffer);

  // Redimensionar e aplicar a cor dominante como fundo
  const resizedImage = await sharp(buffer)
    .resize(1080, 1080, {
      fit: 'contain',
      background: { r: dominantColor.r, g: dominantColor.g, b: dominantColor.b },
    })
    .jpeg()
    .toBuffer();

  return resizedImage;
};

// Middleware para processar JSON no corpo da requisição
app.use(express.json());

// Função para obter arquivo local ou remoto como Buffer
async function getFile(filePath) {
  try {
    if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
      console.log(`Baixando arquivo remoto: ${filePath}`);
      // Baixar arquivo remoto
      const response = await axios.get(filePath, { responseType: 'arraybuffer' });
      const buffer = Buffer.from(response.data);

      console.log(`Arquivo remoto baixado com sucesso. Tamanho: ${buffer.length} bytes`);
      return buffer;
    } else if (fs.existsSync(filePath)) {
      console.log(`Carregando arquivo local: ${filePath}`);
      const extension = path.extname(filePath).toLowerCase();

      // Verificar se o arquivo é um vídeo válido
      const validExtensions = ['.mp4', '.mov', '.avi', '.mkv']; // Adicione outras extensões, se necessário
      if (!validExtensions.includes(extension)) {
        throw new Error(`Arquivo local não é um vídeo válido: ${filePath}`);
      }

      const buffer = fs.readFileSync(filePath);

      console.log(`Arquivo local carregado com sucesso. Tamanho: ${buffer.length} bytes`);
      return buffer;
    } else {
      throw new Error(`Arquivo não encontrado: ${filePath}`);
    }
  } catch (error) {
    console.error(`Erro ao processar o arquivo: ${error.message}`);
    throw error;
  }
}

// Rota para postar no Instagram
app.post('/instagram/post', async (req, res) => {
  try {
      ig.state.generateDevice('guscpcom');
      if (!fs.existsSync('./session.json')) {
          await ig.account.login('dr.economicomics', 'PadraoSS2024!');
          await saveSession();
      } else {
          await restoreSession();
      }

      const { text, type, imageUrls } = req.body;
      if (!text || !type || !imageUrls || imageUrls.length === 0) {
          console.log('Campos ausentes: texto, tipo ou URLs das imagens');
          return res.status(400).send('Campos ausentes: texto, tipo ou URLs das imagens');
      }

      if (type === 'carrossel' && imageUrls.length < 2) {
          console.log('Carrossel precisa de pelo menos duas imagens');
          return res.status(400).send('Carrossel precisa de pelo menos duas imagens');
      }

      // Obter arquivos como Buffer
      const files = await Promise.all(imageUrls.map((filePath) => getFile(filePath)));

      // Publicar no Instagram
      let publishResult;
      if (type === 'feed') {
          publishResult = await ig.publish.photo({
              file: files[0],
              caption: text,
          });
      } else if (type === 'story') {
          publishResult = await ig.publish.story({
              file: files[0],
          });
      } else if (type === 'carrossel') {
          const items = files.map((file) => ({ file }));
          publishResult = await ig.publish.album({
              items,
              caption: text,
          });
      } else if (type === 'reels') {
          console.log('Enviando vídeo como Reels...');
          console.log('Tipo do arquivo carregado:', typeof files[0]);
          console.log('Tamanho do buffer:', files[0]?.length);

          publishResult = await ig.publish.video({
              video: files[0], // Buffer ou stream do vídeo
              caption: text,
          });
          console.log('Vídeo enviado com sucesso:', publishResult);
      } else {
          return res.status(400).send('Tipo de postagem inválido');
      }

      console.log('Postagem no Instagram realizada com sucesso', publishResult);
      res.status(200).send('Postagem no Instagram realizada com sucesso');

  } catch (error) {
      console.error('Erro ao postar no Instagram:', error);
      if (error.response) {
          console.error('Resposta do Instagram:', error.response.data);
      }
      res.status(500).send('Erro ao postar no Instagram');
  }
});

// Rota para postar no WordPress
app.post('/wordpress/post', async (req, res) => {
  try {
    const { title, content, imageUrl } = req.body;

    // Validação dos campos
    if (!title || !content || !imageUrl) {
      console.log('Campos ausentes: título, conteúdo ou URL da imagem');
      return res.status(400).send('Campos ausentes: título, conteúdo ou URL da imagem');
    }

    // Baixar a imagem da URL
    const imageResponse = await axios.get(imageUrl, { responseType: 'arraybuffer' });
    const imageBuffer = Buffer.from(imageResponse.data, 'binary');

    // Upload da imagem como "featured image" usando Basic Auth
    const imageUploadResponse = await axios.post('https://sitesesites.com/wp-json/wp/v2/media', imageBuffer, {
      headers: {
        'Content-Type': 'image/jpeg',
        'Authorization': 'Basic ' + Buffer.from('gustestes:Fl9l Bkuu w0Oh QN62 8H64 ztm1').toString('base64'),
        'Content-Disposition': `attachment; filename="image.jpg"`,
      },
    });

    // Criar o post com a imagem destacada
    const wpResponse = await axios.post('https://sitesesites.com/wp-json/wp/v2/posts', {
      title,
      content,
      featured_media: imageUploadResponse.data.id, // ID da imagem enviada
      status: 'publish',
    }, {
      headers: {
        'Authorization': 'Basic ' + Buffer.from('gustestes:Fl9l Bkuu w0Oh QN62 8H64 ztm1').toString('base64'),
      },
    });

    console.log('Postagem no WordPress realizada com sucesso', wpResponse.data);
    res.status(200).send('Postagem no WordPress realizada com sucesso');
  } catch (error) {
    console.error('Erro ao postar no WordPress', error.response?.data || error.message);
    res.status(500).send('Erro ao postar no WordPress');
  }
});


// Configurações do bot
const config = {
  maxInteractionsPerHour: 30,
  maxInteractionsPerDay: 200,
  profilesToInteract: [
      'walcyrcarrasco',
      'gororoba.narrada',
      'flamenguista.fanaticoo', // Adicione os perfis desejados
  ],
  hashtagsToFollow: [
    'memebrasil',
    'memebrasileiros',
    'humorbrasil',
    'piadas',
    'risos',
    'engracado',
    'comedia',
    'humornegro',
    'zoeira',
    'brincadeiras',
    'humordodia',
    'brasilmemes',
    'zoeiramemes',
    'memezando',
    'vidadehumorista',
    'memesdiarios',
    'humor360',
    'engracados',
    'humorinteligente',
    'memeiro',
    'humoradulto',
    'piadabr',
    'humorbr',
    'divertido',
    'humordehoje',
    'comediabrasil',
    'comediastandup',
    'comediadiaria',
    'brincadeira',
    'memestagram',
    'memebrasiliero',
    'humormemes',
    'comediaengracada',
    'rindomuito',
    'risadas',
    'piadadodia',
    'humordobrasil',
    'memesbrasileiros',
    'memebrasilengracado',
    'comediadiaria',
    'rindoalto',
    'humormemesbr',
    'piadasengracadas',
    'humordodiaengracado',
    'zoeiramemesbr',
    'zoeirabr',
    'memeszoeira',
  ]
};

let interactionCount = 0;

// Função para curtir fotos aleatórias de um perfil
async function likeRandomPhotos(profile) {
    try {
        // Busca o usuário pelo nome do perfil
        const user = await ig.user.searchExact(profile);

        // Obtém o feed do perfil
        const feed = ig.feed.user(user.pk);
        const posts = await feed.items();

        // Verifica se o perfil possui postagens
        if (posts.length > 0) {
            const randomPost = posts[Math.floor(Math.random() * posts.length)];
            
            // Curte uma postagem aleatória
            await ig.media.like({ mediaId: randomPost.id });
            console.log(`Curtiu uma foto de ${profile}`);
            interactionCount++;

            // Segue o perfil
            await ig.friendship.create(user.pk);
            console.log(`Seguiu o perfil de ${profile}`);
        } else {
            console.log(`Nenhuma postagem encontrada para o perfil ${profile}`);
        }
    } catch (error) {
        console.error(`Erro ao curtir e seguir ${profile}:`, error.message);
    }
}
// Função para seguir perfis de uma hashtag
// Função para seguir perfis de uma hashtag
// Função para seguir perfis de uma hashtag
// Função para seguir perfis de uma hashtag
async function followProfilesFromHashtag(hashtag) {
  try {
      console.log(`Buscando perfis da hashtag #${hashtag}...`);
      const feed = ig.feed.tags(hashtag, 'recent');
      const posts = await feed.items();

      if (posts.length > 0) {
          const randomPost = posts[Math.floor(Math.random() * posts.length)];
          const user = randomPost.user;

          if (!user || !user.pk) {
              console.error(`Usuário inválido encontrado na hashtag #${hashtag}.`);
              return;
          }

          console.log(`Tentando seguir o perfil @${user.username} com PK: ${user.pk}`);

          // Realizar a requisição direta ao endpoint
          const response = await ig.request.send({
              url: `/api/v1/friendships/create/${user.pk}/`,
              method: 'POST',
          });

          if (response.status === 'ok') {
              console.log(`Seguiu o perfil @${user.username} da hashtag #${hashtag}`);
              interactionCount++;
          } else {
              console.error(`Erro ao seguir @${user.username}:`, response);
          }
      } else {
          console.log(`Nenhum post encontrado para a hashtag #${hashtag}.`);
      }
  } catch (error) {
      if (error.response?.status === 404) {
          console.error(`Erro 404: Endpoint não encontrado ou perfil não pode ser seguido. Hashtag: #${hashtag}`);
      } else {
          console.error(`Erro ao seguir perfis da hashtag #${hashtag}:`, error.message);
      }
  }
}



// Função principal do bot
async function runBot() {
  if (interactionCount >= config.maxInteractionsPerDay) {
      console.log('Limite diário de interações alcançado. Aguardando reset.');
      return;
  }

  const actions = [
      async () => {
          const randomProfile = config.profilesToInteract[Math.floor(Math.random() * config.profilesToInteract.length)];
          await likeRandomPhotos(randomProfile);
      },
    //   async () => {
    //       const randomHashtag = config.hashtagsToFollow[Math.floor(Math.random() * config.hashtagsToFollow.length)];
    //       await followProfilesFromHashtag(randomHashtag);
    //   },
  ];

  const randomAction = actions[Math.floor(Math.random() * actions.length)];
  await randomAction();
}

// Cron para rodar o bot a cada 5 minutos
console.log("Starting Scheduler from autobot instagram")
cron.schedule('*/* * * * *', async () => {
  if (interactionCount < config.maxInteractionsPerHour) {
      console.log('Executando bot...');
      await runBot();
  } else {
      console.log('Limite de interações por hora alcançado. Aguardando próximo horário.');
  }
});



// Inicia o servidor
app.listen(port, () => {
  console.log(`API rodando na porta ${port}`);
});
