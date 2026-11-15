# Style reference

## Voices
| Character | JP markers | English devices |
|---|---|---|
| Lucia | あたし, ～よ！, えっ！, ～の…？, なにこれ！？ | "I", quick exclamations ("Whoa!", "No way!", "Huh?!"), earnest, a bit flustered; trailing "..." when shy |
| Hanon | あたし, ～じゃん, ～でしょ, teasing ね～ | breezy and sassy: "Come on!", "Seriously?", teasing "Ooh~"; gushes over Mitsuki-sensei |
| Rina | わたし, plain/short だ・だろ, calm | short, cool, matter-of-fact: "Probably Karen.", no gushing |
| Kaito | オレ, ～だろ, ～ぜ | relaxed boy: "Yeah", "C'mon", teasing Lucia gently |
| Hippo | ～です, ～さま, worrying | fussy and formal: "Lucia-sama!", "Honestly!", "Oh dear, oh dear" |
| Villains (Dark Lovers, Black Beauty Sisters) | ～わ, ～ですわ, ～のよ, ウフフ, ホント | theatrical, smug: "Ufufu...", "How pathetic!", "my dears", "Really, you fools!" |
| Meru (child) | ～の！, ～～！ drawn out | childish, pouty: "That's a lie!", "Princess, you big dummy~!" |

## Example pairs
- 2450 `{FA:FF0201}……あれは、マーメイド\nプリンセス！{FA:06}みんな、おうわよ！\n{FA:FF0200}{end}` ->
  `{FA:FF0201}...That's a Mermaid Princess!{FA:06}Everyone, after her!\n{FA:FF0200}{end}` (they chase Karen alone)
- 2451 `{call:@2B8C}{call:@2B0A}・{call:@2B0F}・{call:@2B13}{call:@2B92}おう！{end}` ->
  `{call:@2B8C}{call:@2B0A}, {call:@2B0F}, {call:@2B13}{call:@2B92}Right!{end}`
- 2453 `おそらく、\n{call:@2AAC}だろう。{end}` (Rina) -> `Probably {call:@2AAC}.{end}`
- 2456 `ダーク・ラゔァーズに\nつかまるような、\n{call:@2AAC}じゃないだろ。{end}` (Rina) ->
  `{call:@2AAC} isn't the type to get caught by the Dark Lovers.{end}`
- 2457 `だよね～。{end}` (Hanon) -> `Guess not~.{end}`
- 2459 `{call:@2B8C}{call:@2AAC}{call:@2B92}……のこのこついてきて、ホント\nおまぬけカルテットね！{end}` (the tag says
  Karen, mocking the others) -> `{call:@2B8C}{call:@2AAC}{call:@2B92}...Tagging right along after me. You really
  are a bumbling quartet!{end}`
- 1861 `そんなのウソよ！{wait}わたしは、すいようにママを\n見つけてもらうの！{FA:06}プリンセスさまのバカ～！{end}` (Meru) ->
  `That's a lie!{wait}I'm going to get the water demons to find my mom!{FA:06}Princess, you big dummy~!{end}` (さま on a title -> "Princess", glossary ruling)
  (corrected example: a first draft read すいよう as "the princesses"; it is 水妖 "water demons", the villains. Kana
  text hides kanji words: read the neighbours and the glossary before guessing.)
- 1854 inner thought, framed box: `{call:@2B8C}{call:@2A5B}{call:@2B92}（なにこれ！？\n　ゆうれいが、...）{end}` ->
  `{call:@2B8C}{call:@2A5B}{call:@2B92}(What is this?! A ghost came inside my body...?{FA:06}My body won't listen
  to me at all...){end}` (no `　` indent in English).
