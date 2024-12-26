const puppeteer = require('puppeteer');
const cron = require('node-cron');
const fs = require('fs');

(async () => {
  const sessionFile = 'session.json';

  async function saveSession(page) {
    const cookies = await page.cookies();
    fs.writeFileSync(sessionFile, JSON.stringify(cookies));
    console.log('Sessão salva com sucesso.');
  }

  async function restoreSession(page) {
    if (fs.existsSync(sessionFile)) {
      const cookies = JSON.parse(fs.readFileSync(sessionFile));
      for (const cookie of cookies) {
        await page.setCookie(cookie);
      }
      console.log('Sessão restaurada com sucesso.');
    } else {
      console.log('Nenhuma sessão encontrada. Login será necessário.');
    }
  }

  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  await restoreSession(page);

  await page.goto('https://www.instagram.com/accounts/login/', { waitUntil: 'networkidle2' });
  if (await page.$('input[name="username"]')) {
    await page.type('input[name="username"]', 'dr.economicomics');
    await page.type('input[name="password"]', 'PadraoSS2024!');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle2' });
    console.log('Login realizado com sucesso!');
    await saveSession(page);
  } else {
    console.log('Sessão restaurada, login não necessário.');
  }

  const interactionFile = 'interactions.json';
  const loadInteractions = () => {
    if (fs.existsSync(interactionFile)) {
      return JSON.parse(fs.readFileSync(interactionFile));
    }
    return [];
  };

  const saveInteraction = (postId) => {
    const interactions = loadInteractions();
    if (!interactions.includes(postId)) {
      interactions.push(postId);
      fs.writeFileSync(interactionFile, JSON.stringify(interactions));
    }
  };

  async function likePhotosFromProfile(profileUrl) {
    try {
      await page.goto(profileUrl, { waitUntil: 'networkidle2' });
      const posts = await page.$$('[href*="/p/"]');
      if (posts.length === 0) {
        console.log(`Nenhum post encontrado no perfil: ${profileUrl}`);
        return;
      }

      const likedPosts = [];
      for (let i = 0; i < Math.min(3, posts.length); i++) {
        const randomPost = posts[Math.floor(Math.random() * posts.length)];
        const postUrl = await page.evaluate((el) => el.href, randomPost);
        const postId = postUrl.split('/').filter(Boolean).pop();
        const interactions = loadInteractions();

        if (!interactions.includes(postId)) {
          await page.goto(postUrl, { waitUntil: 'networkidle2' });
          await page.waitForTimeout(3000);
          const likeButton = await page.$('[aria-label="Like"]');
          if (likeButton) {
            await likeButton.click();
            console.log(`Foto curtida: ${postUrl}`);
            saveInteraction(postId);
            likedPosts.push(postUrl);
          } else {
            console.log(`Botão de curtir não encontrado em: ${postUrl}`);
          }
        }
      }

      if (Math.random() <= 0.1 && likedPosts.length > 0) {
        const randomLikedPost = likedPosts[Math.floor(Math.random() * likedPosts.length)];
        await commentOnPost(randomLikedPost, 'Comentário automático de teste!');
      }
    } catch (error) {
      console.error(`Erro ao curtir fotos do perfil: ${error.message}`);
    }
  }

  async function commentOnPost(postUrl, comment) {
    try {
      await page.goto(postUrl, { waitUntil: 'networkidle2' });
      await page.waitForTimeout(3000);
      const commentBox = await page.$('[aria-label="Add a comment..."]');
      if (commentBox) {
        await commentBox.type(comment);
        await page.keyboard.press('Enter');
        console.log(`Comentado na postagem: ${postUrl}`);
      } else {
        console.log(`Campo de comentário não encontrado em: ${postUrl}`);
      }
    } catch (error) {
      console.error(`Erro ao comentar na postagem: ${error.message}`);
    }
  }

  async function followFromHashtag(hashtags) {
    try {
      const randomHashtag = hashtags[Math.floor(Math.random() * hashtags.length)];
      console.log(`Entrando na hashtag: #${randomHashtag}`);
      await page.goto(`https://www.instagram.com/explore/tags/${randomHashtag}/`, { waitUntil: 'networkidle2' });
      await page.waitForTimeout(3000);

      const posts = await page.$$('[href*="/p/"]');
      if (posts.length === 0) {
        console.log(`Nenhum post encontrado para a hashtag #${randomHashtag}`);
        return;
      }

      const randomPost = posts[Math.floor(Math.random() * posts.length)];
      const postUrl = await page.evaluate((el) => el.href, randomPost);
      console.log(`Post aleatório encontrado: ${postUrl}`);

      await page.goto(postUrl, { waitUntil: 'networkidle2' });
      await page.waitForTimeout(3000);

      const profileLink = await page.$('a[href*="/"]');
      if (profileLink) {
        const profileUrl = await page.evaluate((el) => el.href, profileLink);
        console.log(`Entrando no perfil: ${profileUrl}`);

        await page.goto(profileUrl, { waitUntil: 'networkidle2' });
        await page.waitForTimeout(3000);

        const followButton = await page.evaluateHandle(() => {
          const buttons = Array.from(document.querySelectorAll('button'));
          return buttons.find((button) => button.textContent.includes('Follow'));
        });

        if (followButton) {
          await followButton.click();
          console.log('Seguiu o perfil.');
        } else {
          console.log('Já está seguindo ou botão de seguir não encontrado no perfil.');
        }

        await likePhotosFromProfile(profileUrl);
      } else {
        console.log('Perfil não encontrado no post.');
      }
    } catch (error) {
      console.error(`Erro ao seguir de hashtag: ${error.message}`);
    }
  }

  const config = {
    maxInteractionsPerHour: 30,
    hashtags: [
      'memesbrasil',
      'humor',
      'piadas',
      'risadas',
      'memes',
      'engraçado',
      'memezando',
      'zueira',
      'diversão',
      'brincadeiras',
    ],
  };

  let interactionCount = 0;

  async function runBot() {
    if (interactionCount >= config.maxInteractionsPerHour) {
      console.log('Limite de interações por hora alcançado. Aguardando próximo ciclo.');
      return;
    }

    await followFromHashtag(config.hashtags);
    interactionCount++;
  }
  await runBot();
  console.log('Iniciando bot do Instagram com Puppeteer...');
  cron.schedule('*/5 * * * *', async () => {
    console.log('Executando bot...');
    await runBot();
  });
})();
