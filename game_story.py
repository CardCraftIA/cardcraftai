"""Illustrated pilot chapter of CardCraft's original fantasy setting."""
from game_characters import portrait
from game_lore import WORLD

STORY = {
    'Português (BR)': {
        'title': 'Crônicas de Nacarim', 'episode': 'Episódio 1 · O caminho que esqueceu o nome',
        'intro': 'Nas ilhas suspensas de Nacarim, caminhos de luz guardam a memória de quem os percorreu. Quando um caminho se apaga, as lembranças de seu destino começam a desaparecer.',
        'panels': (
            ('spark', '1 · A primeira falha', 'Nilo encontrou uma ponte de luz terminando no vazio. Na sua bússola, o nome da ilha do outro lado havia sumido.'),
            ('anchor', '2 · Uma testemunha', 'Tora lembrava das ondas sob a ponte, mas já não lembrava quem a esperava na outra margem.'),
            ('scout', '3 · O mapa impossível', 'Lume abriu suas asas sobre o mapa: as rotas apagadas desenhavam, juntas, a forma de uma estrela.'),
            ('root', '4 · Uma pista viva', 'Oru ouviu as raízes sob a ilha. Elas repetiam uma palavra antiga: Nacarim não estava perdendo caminhos. Estava pedindo ajuda.'),
            ('wanderer', '5 · A travessia', 'Miri saltou entre duas ilhas sem ponte. Uma trilha de luz surgiu por um instante, guiada por sua coragem.'),
            ('comet', '6 · O chamado', 'Astra viu a estrela acender no céu. “Se lembrarmos juntos, nenhum caminho desaparecerá sozinho.” Continua...'),
        ),
        'footer': 'Ficção e personagens originais do CardCraftAI. As cartas do jogo não representam produtos oficiais dos TCGs do catálogo.',
    },
    'English': {
        'title': 'Chronicles of Nacarim', 'episode': 'Episode 1 · The Path That Forgot Its Name',
        'intro': 'Across Nacarim’s floating islands, paths of light preserve the memories of those who cross them. When a path fades, memories of its destination begin to vanish.',
        'panels': (
            ('spark', '1 · The first break', 'Nilo found a bridge of light ending in empty air. The name of the island beyond had vanished from his compass.'),
            ('anchor', '2 · A witness', 'Tora remembered the waves beneath the bridge, but no longer remembered who waited on the far shore.'),
            ('scout', '3 · The impossible map', 'Lume spread her wings over the map: together, the missing routes formed a star.'),
            ('root', '4 · A living clue', 'Oru listened to the roots below the island. They whispered an old word: Nacarim was not losing paths. It was asking for help.'),
            ('wanderer', '5 · The crossing', 'Miri leapt between two islands without a bridge. A trail of light appeared for a moment, guided by her courage.'),
            ('comet', '6 · The call', 'Astra saw the star kindle in the sky. “If we remember together, no path will disappear alone.” To be continued...'),
        ),
        'footer': 'Original CardCraftAI fiction and characters. These game cards are not official products of the TCGs in the catalog.',
    },
    'Español': {
        'title': 'Crónicas de Nacarim', 'episode': 'Episodio 1 · El camino que olvidó su nombre',
        'intro': 'En las islas flotantes de Nacarim, senderos de luz guardan la memoria de quienes los recorrieron. Cuando uno se apaga, los recuerdos de su destino empiezan a desaparecer.',
        'panels': (
            ('spark', '1 · La primera falla', 'Nilo encontró un puente de luz que terminaba en el vacío. El nombre de la isla de enfrente había desaparecido de su brújula.'),
            ('anchor', '2 · Una testigo', 'Tora recordaba las olas bajo el puente, pero ya no recordaba quién la esperaba en la otra orilla.'),
            ('scout', '3 · El mapa imposible', 'Lume abrió las alas sobre el mapa: las rutas borradas formaban juntas una estrella.'),
            ('root', '4 · Una pista viva', 'Oru escuchó las raíces bajo la isla. Susurraban algo antiguo: Nacarim no perdía caminos. Pedía ayuda.'),
            ('wanderer', '5 · El cruce', 'Miri saltó entre dos islas sin puente. Un sendero de luz apareció por un instante, guiado por su valor.'),
            ('comet', '6 · La llamada', 'Astra vio encenderse la estrella en el cielo. «Si recordamos juntos, ningún camino desaparecerá solo». Continuará...'),
        ),
        'footer': 'Ficción y personajes originales de CardCraftAI. Estas cartas no son productos oficiales de los TCG del catálogo.',
    },
    '日本語': {
        'title': 'ナカリム年代記', 'episode': '第1話 · 名前を忘れた道',
        'intro': '空に浮かぶナカリムの島々では、光の道が旅人たちの記憶を守っている。道が消えると、行き先の記憶も薄れていく。',
        'panels': (
            ('spark', '1 · 最初の異変', 'ニロが見つけた光の橋は、空中で途切れていた。羅針盤から向こうの島の名前も消えていた。'),
            ('anchor', '2 · 証人', 'トラは橋の下の波を覚えていた。でも、向こう岸で待っていた誰かのことは思い出せない。'),
            ('scout', '3 · 不思議な地図', 'ルメが地図の上で翼を広げると、消えた道をつなぐ線が星の形になった。'),
            ('root', '4 · 生きた手がかり', 'オルは島の下の根の声を聞いた。「ナカリムは道を失っているのではない。助けを求めている」。'),
            ('wanderer', '5 · 島を渡る', '橋のない島と島の間をミリが跳んだ。勇気に導かれ、光の道が一瞬だけ現れた。'),
            ('comet', '6 · 呼び声', 'アストラは空に輝く星を見た。「一緒に覚えていれば、どの道も一人では消えない」。つづく…'),
        ),
        'footer': 'CardCraftAI独自の物語とキャラクターです。カタログ内のTCGの公式カードではありません。',
    },
}

MORE_CHAPTERS = {
    'Português (BR)': (
        ('Episódio 2 · A biblioteca de sementes', 'A trilha de Miri levou o grupo ao Bosque. Ali, Pipa guardava uma semente que ainda pronunciava o nome da ilha perdida.', (
            ('sprout', '1 · A voz na semente', '“Isla”, sussurrou a semente. Nilo reconheceu o apelido da irmã. Alguém estivera naquela ilha depois do desaparecimento da ponte.'),
            ('canopy', '2 · O segredo de Varo', 'Varo mostrou um registro proibido: antes da tempestade, as três regiões haviam construído juntas uma máquina para guardar toda lembrança.'),
            ('kiln', '3 · A assinatura de Faro', 'Faro encontrou sua marca nos desenhos da máquina. “Eu fiz os cofres, não a fechadura”, disse. Pela primeira vez, não teve certeza.'),
            ('ember', '4 · A lanterna apagada', 'Brasa iluminou o arquivo, mas uma pena preta atravessou a chama. Um corvo mascarado roubou a semente e levou seu nome escrito numa fita.'),
            ('scout', '5 · O ladrão de nomes', 'Lume perseguiu Corvo Nox até uma ponte invisível. Ele não voava para uma ilha: voava para o espaço vazio entre todas elas.'),
            ('root', '6 · A memória das raízes', 'Oru tocou o chão e ouviu uma criança cantar do outro lado do silêncio. A voz parecia a de Isla. Continua...'))),
        ('Episódio 3 · O arquivo sem vozes', 'Sob as marés do céu, a equipe segue o corvo até o arquivo da Ordem do Branco. As lembranças roubadas brilham em gavetas fechadas.', (
            ('current', '1 · A passagem de Suri', 'Suri encontrou uma corrente que atravessava a pedra. “Pontes também existem embaixo”, disse, guiando todos ao interior do arquivo.'),
            ('tide', '2 · O aviso de Aira', 'Aira leu a maré: se abrissem todas as gavetas de uma vez, as lembranças se perderiam no vento. Precisavam devolver cada história a seu dono.'),
            ('anchor', '3 · A primeira canção', 'Tora ouviu uma melodia dentro de uma caixa. Era a voz que procurava havia tantos anos, mas não a tomou para si: chamou o nome de quem cantava.'),
            ('wanderer', '4 · O mapa vazio', 'O Cartógrafo Oco desenhou a ilha de Miri sem uma única pessoa. Miri escreveu nela os nomes de seus vizinhos, e o papel se rasgou.'),
            ('spark', '5 · Véspera', 'Nilo reconheceu Véspera: a mãe que o deixara na Forja. “Eu quis salvar todos”, disse ela. “Depois, perdi a voz da sua irmã”. A fita em sua mão dizia: Isla.'),
            ('comet', '6 · Uma escolha', 'Astra recusou a chave que controlava o arquivo. “Ninguém pode lembrar por todos.” A estrela acendeu acima das gavetas; cada voz começou a chamar por sua casa. Continua...'))),
    ),
    'English': (
        ('Episode 2 · The Seed Library', 'Miri’s trail led the group into the Grove. There, Pipa kept a seed that could still speak the lost island’s name.', (
            ('sprout', '1 · The seed’s voice', '“Isla,” whispered the seed. Nilo knew his sister’s nickname. Someone had reached that island after its bridge vanished.'),
            ('canopy', '2 · Varo’s secret', 'Varo revealed a forbidden record: before the storm, the three regions built a machine together to preserve every memory.'),
            ('kiln', '3 · Faro’s signature', 'Faro found his mark on its plans. “I built the cases, not the lock,” he said, suddenly uncertain.'),
            ('ember', '4 · The darkened lantern', 'Brasa lit the archive, but a black feather crossed the flame. A masked raven stole the seed and its name ribbon.'),
            ('scout', '5 · The name thief', 'Lume followed Corvo Nox to an invisible bridge. He flew toward no island, but into the emptiness between them.'),
            ('root', '6 · What roots remember', 'Oru touched the ground and heard a child singing beyond the silence. The voice sounded like Isla’s. To be continued...'))),
        ('Episode 3 · The Archive Without Voices', 'Under the sky tides, the group follows the raven to the Order of the Blank. Stolen memories glow in locked drawers.', (
            ('current', '1 · Suri’s passage', 'Suri found a current running through stone. “Bridges exist below, too,” she said, leading them inside.'),
            ('tide', '2 · Aira’s warning', 'Aira read the tide: opening every drawer at once would scatter the memories. Each story had to return to its owner.'),
            ('anchor', '3 · The first song', 'Tora heard the melody she had sought for years. She did not claim it: she called out the singer’s name.'),
            ('wanderer', '4 · The empty map', 'The Hollow Cartographer drew Miri’s island with no people. Miri wrote her neighbors’ names on it, tearing the paper.'),
            ('spark', '5 · Véspera', 'Nilo recognized Véspera, the mother who left him at the Forge. “I wanted to save everyone,” she said. “Then I lost your sister’s voice.” The ribbon read: Isla.'),
            ('comet', '6 · A choice', 'Astra refused the key to control the archive. “No one can remember for everyone.” The star lit up as each voice called for home. To be continued...'))),
    ),
    'Español': (
        ('Episodio 2 · La biblioteca de semillas', 'El rastro de Miri llevó al grupo al Bosque. Allí, Pipa guardaba una semilla que aún decía el nombre de la isla perdida.', (
            ('sprout', '1 · La voz de la semilla', '«Isla», susurró. Nilo reconoció el apodo de su hermana. Alguien había llegado allí tras desaparecer el puente.'),
            ('canopy', '2 · El secreto de Varo', 'Varo mostró un registro prohibido: antes de la tormenta, las tres regiones construyeron una máquina para guardar cada recuerdo.'),
            ('kiln', '3 · La firma de Faro', 'Faro halló su marca en los planos. «Construí las cajas, no la cerradura», dijo, sin estar ya seguro.'),
            ('ember', '4 · El farol apagado', 'Brasa iluminó el archivo, pero una pluma negra cruzó la llama. Un cuervo enmascarado robó la semilla y su cinta con el nombre.'),
            ('scout', '5 · El ladrón de nombres', 'Lume siguió a Corvo Nox hasta un puente invisible. No volaba a una isla, sino al vacío entre todas.'),
            ('root', '6 · Lo que recuerdan las raíces', 'Oru tocó el suelo y oyó a una niña cantar más allá del silencio. Parecía la voz de Isla. Continuará...'))),
        ('Episodio 3 · El archivo sin voces', 'Bajo las mareas del cielo, el grupo sigue al cuervo hasta el archivo de la Orden del Blanco. Los recuerdos robados brillan en cajones cerrados.', (
            ('current', '1 · El paso de Suri', 'Suri encontró una corriente que atravesaba la piedra. «También hay puentes debajo», dijo, guiándolos al interior.'),
            ('tide', '2 · La advertencia de Aira', 'Aira leyó la marea: abrir todos los cajones dispersaría los recuerdos. Cada historia debía volver a su dueño.'),
            ('anchor', '3 · La primera canción', 'Tora oyó la melodía que buscaba desde hacía años. No se la apropió: llamó a quien la cantaba por su nombre.'),
            ('wanderer', '4 · El mapa vacío', 'El Cartógrafo Hueco dibujó la isla de Miri sin personas. Miri escribió los nombres de sus vecinos y rompió el papel.'),
            ('spark', '5 · Véspera', 'Nilo reconoció a Véspera, la madre que lo dejó en la Forja. «Quise salvar a todos. Luego perdí la voz de tu hermana». La cinta decía: Isla.'),
            ('comet', '6 · Una elección', 'Astra rechazó la llave del archivo. «Nadie puede recordar por todos». La estrella se iluminó y cada voz llamó a su hogar. Continuará...'))),
    ),
    '日本語': (
        ('第2話 · 種の図書館', 'ミリの道は一行を森へ導いた。そこには、失われた島の名をまだ語れる種をピパが守っていた。', (
            ('sprout', '1 · 種の声', '「イスラ」と種がささやいた。ニロは妹の愛称だと気づく。橋が消えた後も誰かが島へ渡っていた。'),
            ('canopy', '2 · ヴァロの秘密', 'ヴァロは禁じられた記録を見せた。嵐の前、三つの地域はすべての記憶を守る機械を共に造った。'),
            ('kiln', '3 · ファロの印', '設計図にはファロの印があった。「箱は作った。でも鍵は違う」。その声は揺れた。'),
            ('ember', '4 · 消えた灯', 'ブラサが記録庫を照らすと黒い羽が炎を横切った。仮面のカラスが種と名前のリボンを奪った。'),
            ('scout', '5 · 名を盗む者', 'ルメはコルヴォ・ノクスを見えない橋まで追った。彼は島ではなく、島々の間の空白へ飛んだ。'),
            ('root', '6 · 根の記憶', 'オルが地面に触れると、沈黙の向こうから子どもの歌が聞こえた。イスラの声に似ていた。つづく…'))),
        ('第3話 · 声のない記録庫', '一行は空の潮の下からカラスを追い、白紙の結社の記録庫に着いた。盗まれた記憶が閉じた引き出しの中で光る。', (
            ('current', '1 · スリの通路', 'スリは石を通る流れを見つけた。「橋は下にもあるよ」。皆を内部へ導く。'),
            ('tide', '2 · アイラの警告', '引き出しを一度に開けば記憶は風に散る、とアイラは読んだ。一つずつ持ち主に返さなければ。'),
            ('anchor', '3 · 最初の歌', 'トラは長年探した旋律を聞いた。それを奪わず、歌い手の名前を呼んだ。'),
            ('wanderer', '4 · 空白の地図', '空白の地図師がミリの島を人のいない姿で描いた。ミリが隣人の名を書くと紙が裂けた。'),
            ('spark', '5 · ヴェスペラ', 'ニロはヴェスペラを見て母だと気づいた。「皆を守りたかった。でもあなたの妹の声を見失った」。彼女のリボンにはイスラとあった。'),
            ('comet', '6 · 選択', 'アストラは記録庫を支配する鍵を拒んだ。「誰も皆の代わりには覚えられない」。星が灯り、声が故郷を呼んだ。つづく…'))),
    ),
}


def render_story(st, language='Português (BR)'):
    chapter = STORY.get(language, STORY['English'])
    st.header('📖 ' + chapter['title'])
    origin, villains, destiny = WORLD.get(language, WORLD['English'])
    with st.expander({'Português (BR)': '🌍 Origem, vilões e destino', 'English': '🌍 Origin, villains and destiny',
                      'Español': '🌍 Origen, villanos y destino', '日本語': '🌍 起源・敵・運命'}.get(language, '🌍 World')):
        st.write(origin)
        st.write(villains)
        st.write(destiny)
    episodes = [(chapter['episode'], chapter['intro'], chapter['panels'])] + list(MORE_CHAPTERS.get(language, MORE_CHAPTERS['English']))
    selected = st.selectbox({'Português (BR)': 'Capítulo', 'English': 'Chapter', 'Español': 'Capítulo', '日本語': '章'}.get(language, 'Chapter'),
                            range(len(episodes)), format_func=lambda index: episodes[index][0], key='nacarim_chapter')
    title, intro, panels = episodes[selected]
    st.subheader(title)
    st.write(intro)
    for offset in range(0, len(panels), 2):
        for column, (card, heading, narration) in zip(st.columns(2), panels[offset:offset + 2]):
            with column:
                st.image(portrait(card), width=280)
                st.markdown('**' + heading + '**')
                st.write(narration)
    st.caption(chapter['footer'])
