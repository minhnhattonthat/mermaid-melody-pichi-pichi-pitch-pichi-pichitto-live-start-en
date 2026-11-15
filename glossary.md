# Glossary - Mermaid Melody Pichi Pichi Pitch: Pichi Pichitto Live Start!

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` fails a line whose JP has a term (whole kana/kanji run) but whose English lacks the EN form,
or that uses an Avoid spelling.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Lucia-san, Mitsuki-sensei, Princess-sama is NOT used: さま on a title -> "Lady"/"Princess" per context, on a name -> "-sama"). Name order: Western (given name first).
- Romanisation source: official English names where they exist (Del Rey manga), else Hepburn without macrons.
- Credits: English. Staff names Western order, Hepburn (大内哲也 -> Tetsuya Ouchi).
- Register / flavour: light, bubbly shoujo-anime English for a young audience; contractions; no swearing. Each girl keeps her voice (see Style rules).
- Sound effects / interjections: English equivalents (キャー -> "Eek!", ウフフ -> "Ufufu..." for villains' laughs, アハハ -> "Ahaha!").
- Song lyrics (msgs 256-305, 512-1023, karaoke strip): romaji (Hepburn, no macrons, words spaced as sung, particles は/へ/を as wa/e/o), so the strip matches the sung audio and its colour sweep. Exception to "no macrons" for names: lyrics write long vowels doubled as sung (taiyou, yuuki, arigatou, deshou); the Avoid forms below (Housho, Touin) apply to names only, never "fix" lyrics. Song titles: their official romanised titles; the credits song titles follow the lyrics (Kuro no Kyousoukyoku).
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', … / …… / ・・・ -> "...", ！？ -> "?!", ～ at a line end -> "~" or drop, ♪ ♥ ★ kept (they are in the font).
- Allowed characters: ASCII letters, digits, space and ! ? . , ' " : ; - ( ) [ ] / & ~ * + = % # < > _ plus … ♪ ♥ ★ é. Nothing else (no curly quotes, no em dash: use "--" or "...").
- Lucia (るちあ): cheerful, a bit clumsy, says "あたし"; exclamations ("Whoa!", "No way!"). Hanon (波音): sassy, teasing, boy-crazy. Rina (リナ): cool, calm, mature, short sentences. Kaito: laid-back, teasing boy. Villains (Dark Lovers, Black Beauty Sisters): theatrical, mocking ("Ufufu...", "How pathetic!"). Hippo: fussy little penguin who calls Lucia "Lucia-sama".
- Inner thoughts in （…） stay in ( ). Name tags (【name】) are code, never typed out.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| るちあ / 七海るちあ | Lucia / Lucia Nanami | | pink pearl, Princess of the North Pacific | Luchia / Rucia |
| 波音 / 宝生波音 | Hanon / Hanon Hosho | | aqua pearl, South Atlantic | Hanon Housho |
| リナ / 洞院リナ | Rina / Rina Toin | | green pearl, North Atlantic | Rina Touin |
| かれん | Karen | | purple pearl, Antarctic | |
| ノエル | Noelle | | indigo pearl, Arctic | Noel |
| ココ | Coco | | yellow pearl, South Pacific | |
| 沙羅 | Sara | | orange pearl, Indian Ocean | |
| 海斗 / 堂本海斗 | Kaito / Kaito Domoto | | | Kaitou / Doumoto |
| ヒッポ | Hippo | | Lucia's penguin friend | |
| にこら | Nikora | | owner of the Pearl Piari | Nicola |
| 海月 / 太郎 / 海月せんせい / ミツキ | Mitsuki / Taro / Mitsuki-sensei | | Taro Mitsuki, teacher | Mr. Mitsuki |
| アクア・レジーナ | Aqua Regina | | sea goddess | |
| ガイト | Gaito | | | Gaido |
| イズール | Izuru | | Dark Lovers | Izur |
| エリル | Eriru | | Dark Lovers | Eril |
| ユーリ | Yuri | | Dark Lovers | |
| マリア | Maria | | | |
| シェシェ | Sheshe | | Black Beauty Sisters | Chechet |
| ミミ | Mimi | | Black Beauty Sisters | |
| 芽流 | Meru | | girl looking for her mother | |
| アウリ | Auri | | | |
| タキ | Taki | | | |
| マコト | Makoto | | | |
| モモ | Momo | | | |
| ジェニファー | Jennifer | | | |
| マーメイドプリンセス | Mermaid Princess | | | |
| ？？？ | ??? | | unknown speaker | |
| 雪絵 | Yukie | | Kaito's aunt | |
| 真木 | Maki | | Maki-san | |
| リョウ | Ryo | | | |
| 崎谷 | Sakiya | | | |
| 彩香 | Ayaka | | | |
| 石橋 | Ishibashi | | | |
| 染五郎 | Somegoro | | signs the poem | |
| ジェニファー・ヒューストン | Jennifer Houston | | | |
| サンゴのせい | Coral Spirit | | | |
| なぞのしょうじょ | Mysterious Girl | | name tag | |
| こいぬ | Puppy | | name tag | |
| かんきゃく | Audience | | name tag | |
| アナウンサー | Announcer | | name tag | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| パールピアリ / プチホテル・パールピアリ | Pearl Piari / Petit Hotel Pearl Piari | | Nikora's hotel | |
| パンタラッサ | Panthalassa | | Gaito's castle | |
| シーパーク | Sea Park | | | |
| にんげんかい | human world | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| すいよう / 水妖 | water demon | | 水妖, Gaito's sea monsters (written in kana) | |
| ダーク・ラゔァーズ | Dark Lovers | | Izuru, Eriru, Yuri | |
| ブラック・ビューティー・シスターズ | Black Beauty Sisters | | Sheshe and Mimi | |
| ピチピチボイス | Pichi Pichi Voice | | transformation call | |
| ぴちぴち / ピチピチ | Pichi Pichi | | on its own (show's catchword): capitalised like the title | pichi-pichi |
| きゃあ / キャー | Eek / Eee | | Eek for a scream, Eee~ for a squeal of delight | Kyaa / Kyaaa |
| ラブシャワーピッチ | Love Shower Pitch | | finishing call | |
| マーメイドビーズ | Mermaid Beads | | | |
| ライブスタート | Live Start | | | |
| ライブコンサート | live concert | | | |
| アンコール | encore | | | |
| ペンダント | pendant | | holds the pearl | |
| ラゔァーズ・アイス・ダンス | Lovers Ice Dance | | | Lovers' Ice Dance |
| ダーク・ラゔァーズ・ブリリアント・コンビネーション | Dark Lovers Brilliant Combination | | | |
| ありあけのつきのオルゴール | Dawn Moon Music Box | | | |
| ゆめみせき | Dreamstone | | | |
| にんぎょのひとみ | Mermaid's Eye | | jewel | |
| セイレーンのつぼ | Siren's Jar | | | |
| ねがいのゆびわ | Ring of Wishes | | | |
| ヒポカンポス | Hippocampus | | | |
| ダークなべ / やみなべ | Dark Hot Pot | | pun on Dark Lovers | |
| マーメイドコンテスト | Mermaid Contest | | | |
| きもだめし | test of courage | | | |

## Decisions from earlier batches
- `{call:@2B27}` draws "Mermaid Princess": no `s` glued on (the check fails it). Plural: write "Mermaid Princesses" out in place of the call, or singular when the JP is singular.
- ガイトさま -> "Gaito-sama" (call or plain text as the JP has it), never "Lord Gaito".
- ラブ②シャワーピッチ -> "Love Love Shower Pitch" (② = circled 2 in the font, read as the repeat mark; the Japanese font has no heart, the English font does). Plain ラブシャワーピッチ = "Love Shower Pitch".
- キャー: "Eek!" for a scream, "Eee~!" for a squeal of delight.
- Lyrics: katakana loanwords that are English words stay English with a capital (Melody, Stage, Kiss); Japanese-ised loans sung as Japanese stay romaji (doa, yotto, orugooru, garasu).
- Song title 黒の協奏曲~concerto~ = "Kuro no Kyousoukyoku ~concerto~" in credits; Mimi's profile reads it くろのコンチェルト -> "Kuro no Concerto".
- Children's おねえちゃん/おにいちゃん + name: "Big Sis Lucia" / "Big Bro Kaito"; alone: "Sis".
- Auri's っす tic: "yo", at most one per line.
