"""Illustrated pilot chapter of CardCraft's original fantasy setting."""
from game_characters import portrait

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


def render_story(st, language='Português (BR)'):
    chapter = STORY.get(language, STORY['English'])
    st.header('📖 ' + chapter['title'])
    st.subheader(chapter['episode'])
    st.write(chapter['intro'])
    for offset in range(0, len(chapter['panels']), 2):
        for column, (card, heading, narration) in zip(st.columns(2), chapter['panels'][offset:offset + 2]):
            with column:
                st.image(portrait(card), width=280)
                st.markdown('**' + heading + '**')
                st.write(narration)
    st.caption(chapter['footer'])
