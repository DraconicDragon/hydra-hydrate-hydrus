# fmt: off
# ruff: noqa
# pyright: reportUndefinedVariable=false

#
# Some common values used in the default import job
# You probably want to change these
#

# region: default config
defAPIURL = "http://127.0.0.1:45869"
defAPIKey = "the key of keys"
defTagRepos = ["downloader tags"]
defTagReposForNonUrlSources = ["downloader tags"]
defTagReposTwitter = ["twitter tags"]
defTagReposPixiv = ["pixiv tags"]
# These are the defaults that Hydrus automatically creates,
# you'll have to add here any others that appear in the importer configuration.
# You can get the key from Hydrus in the review services window.
defServiceNamesToKeys = {
  "my tags": "6c6f63616c2074616773",
  "local tags": "6c6f63616c2074616773",
  "downloader tags": "646f776e6c6f616465722074616773",
  "twitter tags": "",
  "pixiv tags": ""
}
# This function will be applied to the final results generated from each file
# You can implement any global blacklists/whitelists or transformations here
def defGlobalResultFilter(abspath: str, json_data: dict, tags: set[tuple[str, str]], urls: list[str], notes: set[tuple[str, str]], domain_times: dict[str, datetime]):
    return tags, urls, notes, domain_times
# endregion

#
# region: Default import job - main config
#

j = ImportJob(name = "default",
              apiURL = defAPIURL,
              apiKey = defAPIKey,
              usePathBasedImport = False,
              overridePathBasedLocation = "",
              orderFolderContents = "name",
              nonUrlSourceNamespace = "hydl-non-url-source",
              serviceNamesToKeys = defServiceNamesToKeys,
              globalResultFilter = defGlobalResultFilter)

#
# Default import job - generic tag/URL rules (applicable for all sites)
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: True)

g.tags(name = 'hydownloader import job datetime', tagRepos = defTagRepos).values(lambda: 'hydl-import-time:'+import_start_datetime)

g.tags(name = 'additional tags (with tag repo specified)', allowNoResult = True) \
 .values(lambda: [repo+':'+tag for (repo,tag) in get_namespaces_tags(extra_tags, '', None) if repo != '' and repo != 'urls'])

g.tags(name = 'additional tags (without tag repo specified)', tagRepos = defTagRepos, allowNoResult = True) \
 .values(lambda: extra_tags[''] if '' in extra_tags else [])

g.tags(name = 'hydownloader IDs', tagRepos = defTagRepos) \
 .values(lambda: ['hydl-sub-id:'+s_id for s_id in sub_ids]) \
 .values(lambda: ['hydl-url-id:'+u_id for u_id in url_ids])

g.tags(name = 'hydownloader source site', tagRepos = defTagRepos) \
 .values(lambda: 'hydl-src-site:'+json_data['category'])

g.urls(name = 'additional URLs', allowNoResult = True) \
 .values(lambda: extra_tags['urls'])

# i dont want/need this because 1. i dont see what its good for (in my case) 2. it doesnt work with danbooru ordfav:user sorting and spits out "[...]/posts?page=1"
# g.urls(name = 'source URLs from single URL queue', allowNoResult = True) \
#  .values(lambda: single_urls)

g.urls(name = 'gallery-dl file url', allowEmpty = True) \
 .values(lambda: (u := json_data.get('gallerydl_file_url', '')) and ('' if u.startswith('text:') else u))
#endregion

#
# region: pixiv
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/pixiv/'))

g.tags(name = 'pixiv tags (original), new json format', tagRepos = defTagReposPixiv, allowNoResult = True, allowTagsEndingWithColon = True) \
 .values(lambda: [(tag if type(tag) is str else tag['name']) for tag in json_data['tags']] if not 'untranslated_tags' in json_data else [])

g.tags(name = 'pixiv tags (translated), new json format', tagRepos = defTagReposPixiv, allowNoResult = True, allowTagsEndingWithColon = True) \
 .values(lambda: [tag['translated_name'] for tag in json_data['tags'] if type(tag) is not str and tag['translated_name'] is not None] if not 'untranslated_tags' in json_data else [])

g.tags(name = 'pixiv tags (original), old json format', tagRepos = defTagReposPixiv, allowNoResult = True, allowTagsEndingWithColon = True) \
 .values(lambda: json_data['untranslated_tags'] if 'untranslated_tags' in json_data else [])

g.tags(name = 'pixiv tags (translated), old json format', tagRepos = defTagReposPixiv, allowNoResult = True, allowTagsEndingWithColon = True) \
 .values(lambda: json_data['tags'] if 'untranslated_tags' in json_data else [])

g.tags(name = 'pixiv generated tags', tagRepos = defTagReposPixiv) \
 .values(lambda: 'page:'+str(int(json_data['suffix'][2:])+1) if json_data['suffix'] else 'page:1') \
 .values(lambda: 'pixiv work:'+str(json_data['id'])) \
 .values(lambda: 'creator:'+json_data['user']['account']) \
 .values(lambda: 'creator:'+json_data['user']['name']) \
 .values(lambda: 'rating:'+json_data['rating']) \
 .values(lambda: 'pixiv id:'+str(json_data['user']['id']))

g.tags(name = 'pixiv source tag', tagRepos = defTagRepos) \
 .values(lambda: 'source:pixiv')

g.tags(name = 'pixiv generated tags (title)', tagRepos = defTagReposPixiv, allowEmpty = True, allowTagsEndingWithColon = True) \
 .values(lambda: ('title:'+json_data['title']) if json_data['title'] and json_data['title'].strip() else '')

g.urls(name = 'pixiv artwork url') \
 .values(lambda: 'https://www.pixiv.net/en/artworks/'+str(json_data['id']))

g.notes(name = 'pixiv caption') \
 .values(lambda: assemble_note(json_data, 'pixiv caption', ['title'], ['caption']))
# endregion

#
# region: nijie.info
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/nijie/'))

g.tags(name = 'nijie tags', tagRepos = defTagRepos, allowNoResult = True) \
 .values(lambda: json_data['tags'])

g.tags(name = 'nijie generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'title:'+json_data['title']) \
 .values(lambda: 'page:'+str(json_data['num'])) \
 .values(lambda: 'nijie id:'+str(json_data['image_id'])) \
 .values(lambda: 'creator:'+json_data['artist_name']) \
 .values(lambda: 'nijie artist id:'+str(json_data['artist_id']))

g.urls(name = 'nijie urls') \
 .values(lambda: 'https://nijie.info/view.php?id='+str(json_data['image_id'])) \
 .values(lambda: json_data['url'])

g.notes(name = 'nijie description') \
 .values(lambda: assemble_note(json_data, 'nijie description', ['title'], ['description']))
# endregion

#
# region: Patreon
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/patreon/'))

g.tags(name = 'patreon generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'page:'+str(json_data['num'])) \
 .values(lambda: 'patreon id:'+str(json_data['id'])) \
 .values(lambda: 'creator:'+json_data['creator']['full_name']) \
 .values(lambda: 'creator:'+json_data['creator']['vanity']) \
 .values(lambda: 'patreon artist id:'+str(json_data['creator']['id']))

g.tags(name = 'patreon generated tags (title)', tagRepos = defTagRepos, allowEmpty = True, allowTagsEndingWithColon = True) \
 .values(lambda: ('title:'+json_data['title']) if json_data['title'] and json_data['title'].strip() else '')

g.urls(name = 'patreon urls') \
 .values(lambda: json_data['url'])

g.notes(name = 'patreon description') \
 .values(lambda: assemble_note(json_data, 'patreon description', ['title'], ['content']))
# endregion

#
# region: Newgrounds
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/newgrounds/'))

g.tags(name = 'newgrounds tags', tagRepos = defTagRepos, allowNoResult = True) \
 .values(lambda: json_data['tags'])

g.tags(name = 'newgrounds generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'title:'+json_data['title']) \
 .values(lambda: 'creator:'+json_data['user']) \
 .values(lambda: 'rating:'+json_data['rating']) \
 .values(lambda: ('creator:'+artist for artist in json_data['artist']))

g.urls(name = 'newgrounds url') \
 .values(lambda: json_data['url'])

g.urls(name = 'newgrounds post url') \
 .values(lambda: json_data['post_url'])

g.notes(name = 'newgrounds description') \
 .values(lambda: assemble_note(json_data, 'newgrounds description', ['title'], ['description'], skip_if_empty_content = True))

g.notes(name = 'newgrounds comment') \
 .values(lambda: assemble_note(json_data, 'newgrounds comment', ['title'], ['comment'], skip_if_empty_content = True))
# endregion

#
# region: Mastodon instances
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/mastodon/'))

g.tags(name = 'mastodon tags', tagRepos = defTagRepos, allowNoResult = True) \
 .values(lambda: json_data['tags'])

g.tags(name = 'mastodon generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'mastodon instance:'+json_data['instance']) \
 .values(lambda: 'mastodon id:'+str(json_data['id'])) \
 .values(lambda: 'creator:'+json_data['account']['username']) \
 .values(lambda: 'creator:'+json_data['account']['acct']) \
 .values(lambda: 'creator:'+json_data['account']['display_name'])

g.urls(name = 'mastodon urls') \
 .values(lambda: json_data['url']) \
 .values(lambda: json_data['uri'])

g.notes(name = 'mastodon content') \
 .values(lambda: "mastodon content\n"+str(json_data["content"]))
# endregion

#
# region: misskey instances
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/misskey/'))

g.tags(name = 'misskey tags', tagRepos = defTagRepos, allowNoResult = True) \
 .values(lambda: json_data['tags'] if 'tags' in json_data else [])

g.tags(name = 'misskey generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'misskey instance:'+json_data['instance']) \
 .values(lambda: 'misskey id:'+str(json_data['id'])) \
 .values(lambda: 'creator:'+json_data['user']['username']) \
 .values(lambda: 'misskey user id:'+json_data['userId']) \
 .values(lambda: 'misskey file id:'+json_data['file']['id'])

g.tags(name = 'misskey generated tags', tagRepos = defTagRepos, skipOnError = True) \
 .values(lambda: 'creator:'+json_data['user']['name'])

g.urls(name = 'misskey urls') \
 .values(lambda: json_data['file']['url']) \
 .values(lambda: 'https://'+json_data['instance']+'/notes/'+json_data['id'])

g.notes(name = 'misskey content') \
 .values(lambda: "misskey content\n"+str(json_data["content"]))
# endregion

#
# region: WebToons
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/webtoons/'))

g.tags(name = 'webtoons generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'webtoons comic:'+json_data['comic']) \
 .values(lambda: 'chapter number:'+json_data['episode']) \
 .values(lambda: 'chapter:'+json_data['title']) \
 .values(lambda: 'page:'+str(json_data['num']))

g.urls(name = 'webtoons urls') \
 .values(lambda: 'https://www.webtoons.com/'+json_data['lang']+'/'+json_data['genre']+'/'+json_data['comic']+'/list?title_no='+json_data['title_no'])
# endregion

#
# region: danbooru
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/danbooru/'))

g.tags(name = 'danbooru generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'danbooru id:'+str(json_data['id'])) \
 .values(lambda: 'source:danbooru') \
 .values(lambda: 'rating:' + {'g': 'general', 's': 'sensitive', 'e': 'explicit', 'q': 'questionable'}.get(json_data['rating'], json_data['rating'])) \
 .values(lambda: ('pixiv work:'+str(json_data['pixiv_id'])) if json_data['pixiv_id'] else '') \
 .values(lambda: ('danbooru_parent:'+str(json_data['parent_id'])) if json_data.get('parent_id') else '') \
 .values(lambda: 'danbooru_has_children:true' if json_data.get('has_children') else '') \
 .values(lambda: 'page:c2' if json_data.get('parent_id') else '')   # hardcoded marker for child posts

g.domain_time('danbooru.donmai.us', lambda: json_data['created_at'])

g.tags(name = 'danbooru tags', tagRepos = defTagRepos, allowTagsEndingWithColon = True) \
 .values(lambda: [(key+':'+tag if key != 'general' else tag) for (key, tag) in get_namespaces_tags(json_data, 'tag_string_')])

g.urls(name = 'danbooru urls', allowEmpty = True) \
 .values(lambda: 'https://danbooru.donmai.us/posts/'+str(json_data['id'])) \
 .values(lambda: json_data['source'])
# .values(lambda: json_data['large_file_url']) \ # this is sample
# .values(lambda: json_data['file_url']) \

# ---- Additional metadata ----

### IMPORTANT: Hydrus separates notes into 'name' (header) and content/body by looking for the first newline. 

# Creates a note for "Artist Commentary" with header = original_title (fallback to default) and body = original_description
g.notes(name = 'danbooru artist commentary', allowEmpty=True, allowNoResult = True) \
  .values(lambda:
    ([(c.get('original_title') or 'Danbooru Artist Commentary') +
      (('\n' + c.get('original_description')) if c.get('original_description') else '')]
     if (c := json_data.get('artist_commentary')) and (c.get('original_title') or c.get('original_description'))
     else [])
  )

# Creates a second, separate note for the translated commentary with header = translated_title and body = translated_description
g.notes(name='translated danbooru artist commentary', allowEmpty=True, allowNoResult=True) \
  .values(lambda:
    ([( (title := c.get('translated_title')) and title + " (TL'd)" or 'Translated Danbooru Artist Commentary') +
      (('\n' + c.get('translated_description')) if c.get('translated_description') else '')]
     if (c := json_data.get('artist_commentary')) and (c.get('translated_title') or c.get('translated_description'))
     else [])
  )

g.notes(name = 'danbooru notes', allowNoResult = True) \
 .values(lambda: [] if not json_data['notes'] else "danbooru notes\n"+json.dumps(json_data['notes'], indent=4))
# .values(lambda: assemble_note(json_data, 'danbooru artist commentary', ['artist_commentary','original_title'], ['artist_commentary','original_description'])) \
# .values(lambda: assemble_note(json_data, 'translated danbooru artist commentary', ['artist_commentary','translated_title'], ['artist_commentary','translated_description'])) \

# endregion

#
# region: aibooru
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/aibooru/'))

g.tags(name = 'aibooru generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'aibooru id:'+str(json_data['id'])) \
 .values(lambda: 'booru:aibooru') \
 .values(lambda: ('pixiv work:'+str(json_data['pixiv_id'])) if json_data['pixiv_id'] else '')

g.domain_time('aibooru.online', lambda: json_data['created_at'])

g.tags(name = 'aibooru tags', tagRepos = defTagRepos, allowTagsEndingWithColon = True) \
 .values(lambda: [(key+':'+tag if key != 'general' else tag) for (key, tag) in get_namespaces_tags(json_data, 'tag_string_')])

g.urls(name = 'aibooru urls', allowEmpty = True) \
 .values(lambda: json_data['file_url']) \
 .values(lambda: json_data['large_file_url']) \
 .values(lambda: 'https://aibooru.online/posts/'+str(json_data['id'])) \
 .values(lambda: json_data['source'])
# endregion

#
# region: atfbooru
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/atfbooru/'))

g.tags(name = 'atfbooru generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'atfbooru id:'+str(json_data['id'])) \
 .values(lambda: 'booru:atfbooru') \
 .values(lambda: ('pixiv work:'+str(json_data['pixiv_id'])) if json_data['pixiv_id'] else '')

g.tags(name = 'atfbooru tags', tagRepos = defTagRepos, allowTagsEndingWithColon = True) \
 .values(lambda: [(key+':'+tag if key != 'general' else tag) for (key, tag) in get_namespaces_tags(json_data, 'tag_string_')])

g.urls(name = 'atfbooru urls', allowEmpty = True) \
 .values(lambda: json_data['file_url']) \
 .values(lambda: json_data['large_file_url']) \
 .values(lambda: 'https://booru.allthefallen.moe/posts/'+str(json_data['id'])) \
 .values(lambda: json_data['source'])

g.notes(name = 'atfbooru artist commentary and notes', allowNoResult = True) \
 .values(lambda: assemble_note(json_data, 'atfbooru artist commentary', ['artist_commentary','original_title'], ['artist_commentary','original_description'])) \
 .values(lambda: assemble_note(json_data, 'atfbooru artist commentary (translated)', ['artist_commentary','translated_title'], ['artist_commentary','translated_description'])) \
 .values(lambda: [] if not json_data['notes'] else "atfbooru notes\n"+json.dumps(json_data['notes'], indent=4))
# endregion

#
# region: gelbooru
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/gelbooru/'))

g.tags(name = 'gelbooru generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'gelbooru id:'+str(json_data['id'])) \
 .values(lambda: 'booru:gelbooru') \
 .values(lambda: 'rating:'+json_data['rating']) \
 .values(lambda: ('title:'+json_data['title']) if json_data['title'] and json_data['title'].strip() else '')

g.domain_time('gelbooru.com', lambda: json_data['created_at'])

g.tags(name = 'gelbooru tags', tagRepos = defTagRepos, allowTagsEndingWithColon = True) \
 .values(lambda: [(key+':'+tag if key != 'general' else tag) for (key, tag) in get_namespaces_tags(json_data, 'tags_')])

g.urls(name = 'gelbooru urls', allowEmpty = True) \
 .values(lambda: json_data['file_url']) \
 .values(lambda: 'https://gelbooru.com/index.php?page=post&s=view&id='+str(json_data['id'])) \
 .values(lambda: json_data['source'])

g.notes(name = 'gelbooru notes', allowNoResult = True) \
 .values(lambda: [] if not json_data['notes'] else "gelbooru notes\n"+json.dumps(json_data['notes'], indent=4))
# endregion

#
# region: Sankaku
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/sankaku/'))

g.tags(name = 'sankaku generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'sankaku id:'+str(json_data['id'])) \
 .values(lambda: 'booru:sankaku') \
 .values(lambda: 'rating:'+json_data['rating'])

g.tags(name = 'sankaku tags', tagRepos = defTagRepos, allowTagsEndingWithColon = True) \
 .values(lambda: [(key+':'+tag if key != 'general' else tag) for (key, tag) in get_namespaces_tags(json_data, 'tags_', None)])
# old, broken since they started using spaces instead of _ inside tags in these strings
# .values(lambda: [(key+':'+tag if key != 'general' else tag) for (key, tag) in get_namespaces_tags(json_data, 'tag_string_')])

g.urls(name = 'sankaku urls', allowEmpty = True) \
 .values(lambda: json_data['file_url']) \
 .values(lambda: 'https://chan.sankakucomplex.com/en/posts/'+str(json_data['id'])) \
 .values(lambda: json_data['source'] if json_data['source'] else '')
# endregion

#
# region: Sankaku idolcomplex
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/idolcomplex/'))

g.tags(name = 'idolcomplex generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'idolcomplex id:'+str(json_data['id'])) \
 .values(lambda: 'booru:idolcomplex') \
 .values(lambda: 'rating:'+json_data['rating'])

g.tags(name = 'idolcomplex tags', tagRepos = defTagRepos) \
 .values(lambda: [(key+':'+tag if key != 'general' else tag) for (key, tag) in get_namespaces_tags(json_data, 'tags_')])

g.urls(name = 'idolcomplex urls', allowEmpty = True) \
 .values(lambda: json_data['file_url']) \
 .values(lambda: 'https://idol.sankakucomplex.com/post/show/'+str(json_data['id']))
# endregion

#
# region: HentaiFoundry
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/hentaifoundry/'))

g.tags(name = 'hentaifoundry generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'title:'+json_data['title']) \
 .values(lambda: 'medium:'+json_data['media'] if 'media' in json_data else [])

g.tags(name = 'hentaifoundry tags', tagRepos = defTagRepos) \
 .values(lambda: [tag.replace('_',' ') for tag in json_data['tags']] if 'tags' in json_data else []) \
 .values(lambda: json_data['ratings'])

g.urls(name = 'hentaifoundry urls') \
 .values(lambda: json_data['src']) \
 .values(lambda: 'https://www.hentai-foundry.com/pictures/user/'+json_data['user']+'/'+str(json_data['index']))

g.notes(name = 'hentaifoundry description') \
 .values(lambda: assemble_note(json_data, 'hentaifoundry description', ['title'], ['description']))
# endregion

#
# region: Deviantart
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/deviantart/'))

g.tags(name = 'deviantart generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'title:'+json_data['title']) \
 .values(lambda: 'creator:'+json_data['username'])

g.tags(name = 'deviantart tags', tagRepos = defTagRepos, allowNoResult = True) \
 .values(lambda: json_data['tags'])

g.urls(name = 'deviantart urls', allowEmpty = True) \
 .values(lambda: json_data['content']['src'] if 'content' in json_data else '') \
 .values(lambda: json_data['target']['src'] if 'target' in json_data else '') \
 .values(lambda: json_data['url'])
# endregion

#
# region: Twitter
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/twitter/') and pathlen(path) > 3)

g.tags(name = 'twitter generated tags', tagRepos = defTagReposTwitter) \
 .values(lambda: 'creator:'+json_data['author']['name']) \
 .values(lambda: 'creator:twitterid:'+str(json_data['author']['id'])) \
 .values(lambda: 'tweet id:'+str(json_data['tweet_id']))
# .values(lambda: 'creator:'+json_data['author']['nick'])
# NOTE: 'nick' is display name, sometimes japanese artists have japanese letters for nick and latin letter variant as handle
# generally i dont like to have all 3 (id, handle, nick/display name) but nick can overlap with pixiv name
# but also i dont really want my source to be twitter in the first place if it exists anywhere else because twitter compression is awful
# I'll leave it commented in

g.urls(name = 'twitter urls') \
 .values(lambda: 'https://twitter.com/'+json_data['author']['name']+'/status/'+str(json_data['tweet_id']))
# .values(lambda: 'https://twitter.com/i/status/'+str(json_data['tweet_id'])) \

g.tags(name = 'extra twitter generated tags', tagRepos = defTagReposTwitter, allowEmpty = True) \
 .values(lambda: 'page:'+str(json_data['num']) if json_data['count'] > 1 else '') \
 .values(lambda: 'twitter_gif' if ('bitrate' in json_data and json_data['bitrate'] == 0) else '')
# .values(lambda: 'reply to:' + json_data['reply_to'] if 'reply_to' in json_data else '') \

g.tags(name = 'twitter source tag', tagRepos = defTagRepos) \
 .values(lambda: 'source:twitter')

g.tags(name = 'tweet hashtags', tagRepos = defTagReposTwitter, allowEmpty = True, ) \
 .values(lambda: ['tweet hashtag:' + hashtag for hashtag in json_data['hashtags']] if 'hashtags' in json_data else '')

g.notes(name = 'tweet text', allowEmpty = True) \
 .values(lambda: "tweet text\n"+json_data['content'])

g.domain_time('x.com', lambda: json_data['date'])
g.domain_time('twitter.com', lambda: json_data['date'])
# endregion

#
# region: Bluesky
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/bluesky/'))

g.tags(name = 'bluesky generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'creator:'+json_data['author']['handle']) \
 .values(lambda: 'bluesky instance:'+json_data['instance']) \
 .values(lambda: json_data['hashtags']) \
 .values(lambda: 'bluesky post id:'+json_data['post_id'])

g.tags(name = 'bluesky author display name', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'creator:'+json_data['author']['displayName'] if json_data['author']['displayName'] else '')

g.urls(name = 'bluesky urls') \
 .values(lambda: "https://"+json_data['instance']+"/profile/"+json_data['user']['handle']+"/post/"+json_data['post_id'])

g.notes(name = 'bluesky post text and description', allowEmpty = True) \
 .values(lambda: "post text\n"+json_data['text']) \
 .values(lambda: "post description\n"+json_data['description'])

g.domain_time(lambda: json_data['instance'], lambda: json_data['createdAt'])
# endregion

#
# region: kemono
#

# everything but discord (discord entries lack most of the metadata used here)
g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: (pstartswith(path, 'gallery-dl/kemonoparty/') or pstartswith(path, 'gallery-dl/kemono/')) and json_data['subcategory'] != 'discord')

g.tags(name = 'kemono generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'title:'+json_data['title']) \
 .values(lambda: 'creator:'+json_data['username'] if 'username' in json_data else '') \
 .values(lambda: 'kemono service:'+json_data['service']) \
 .values(lambda: 'kemono id:'+json_data['id']) \
 .values(lambda: 'kemono uid:'+json_data['user']) \
 .values(lambda: '{} id:{}'.format(('pixiv' if json_data['service'] == 'fanbox' else json_data['service']), json_data['user']))

# non-discord post URL
g.urls(name='kemono post url') \
 .values(lambda: 'https://kemono.cr/' + json_data['service'] + '/user/' + json_data['user'] + '/post/' + json_data['id'])

# discord
g = j.group(filter=lambda: pstartswith(path, 'gallery-dl/kemonoparty/discord/') or pstartswith(path, 'gallery-dl/kemono/discord/'))

g.tags(name='kemonoparty discord generated tags', tagRepos = defTagRepos, allowNoResult = True, allowTagsEndingWithColon = True) \
 .values(lambda: json_value_with_namespace(json_data, 'id', 'discord post id')) \
 .values(lambda: 'page:{}'.format(json_data['num']) if json_data['type'] in {'attachment', 'inline'} else ()) \
 .values(lambda: 'filename:{}'.format(json_data['filename']) if 'filename' in json_data else ()) \
 .values(lambda: json_value_with_namespace(json_data, 'channel_name', 'discord channel')) \
 .values(lambda: json_value_with_namespace(json_data, 'server', 'discord server')) \
 .values(lambda: 'uploader:' + json_data['author']['username'])
# the following adds whoever posted the image to discord as creator, which isn't necessarily the same as the actual creator
# add this rule at your own risk
# .values(lambda: 'creator:' + json_data['author']['username'])

g.urls(name='kemono discord post url') \
 .values(lambda: 'https://kemono.cr/discord/server/{}'.format(json_data['server']))
# endregion

#
# region: coomer.party
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/coomerparty/') or pstartswith(path, 'gallery-dl/coomer/'))

g.tags(name = 'coomerparty generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'title:'+json_data['title']) \
 .values(lambda: 'person:'+json_data['username']) \
 .values(lambda: 'coomer.party service:'+json_data['service']) \
 .values(lambda: 'coomer.party id:'+json_data['id']) \
 .values(lambda: 'coomer.party user id:'+json_data['user'])

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/directlink/'))

g.urls(name = 'directlink url') \
 .values(lambda: clean_url('https://'+json_data['domain']+'/'+json_data['path']+'/'+json_data['filename']+'.'+json_data['extension']))
# endregion

#
# region: 3dbooru
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/3dbooru/'))

g.tags(name = '3dbooru generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'creator:'+json_data['author']) \
 .values(lambda: 'booru:3dbooru') \
 .values(lambda: '3dbooru id:'+str(json_data['id'])) \
 .values(lambda: 'rating:'+json_data['rating'])

g.tags(name = '3dbooru tags', tagRepos = defTagRepos) \
 .values(lambda: [(key+':'+tag if key != 'general' else tag) for (key, tag) in get_namespaces_tags(json_data)])

g.urls(name = '3dbooru URLs') \
 .values(lambda: json_data['file_url']) \
 .values(lambda: 'http://behoimi.org/post/show/'+str(json_data['id']))
# endregion

#
# region: safebooru
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/safebooru/'))

g.tags(name = 'safebooru generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'safebooru id:'+json_data['id']) \
 .values(lambda: 'booru:safebooru') \
 .values(lambda: 'rating:'+json_data['rating'])

g.domain_time('safebooru.org', lambda: json_data['created_at'])

g.tags(name = 'safebooru tags', tagRepos = defTagRepos) \
 .values(lambda: map(lambda x: x.strip().replace('_', ' '),json_data['tags'].strip().split(' ')))

g.urls(name = 'safebooru URLs', allowEmpty = True) \
 .values(lambda: json_data['file_url']) \
 .values(lambda: 'https://safebooru.org/index.php?page=post&s=view&id='+json_data['id']) \
 .values(lambda: json_data['source'])
# endregion

#
# region: Tumblr
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/tumblr/'))

g.tags(name = 'tumblr generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'tumblr blog:'+json_data['blog_name'])

g.tags(name = 'tumblr tags', tagRepos = defTagRepos, allowNoResult = True) \
 .values(lambda: json_data['tags'])

g.urls(name = 'tumblr URLs', allowEmpty = True) \
 .values(lambda: json_data['short_url']) \
 .values(lambda: json_data['post_url']) \
 .values(lambda: json_data['photo']['url'] if 'photo' in json_data else '') \
 .values(lambda: json_data['image_permalink'] if 'image_permalink' in json_data else '')
# endregion

#
# region: Fantia
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/fantia/'))

g.tags(name = 'fantia generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: ('title:'+json_data['content_title'] if 'content_tile' in json_data and json_data['content_title'] else '')) \
 .values(lambda: 'title:'+json_data['post_title']) \
 .values(lambda: 'rating:'+json_data['rating']) \
 .values(lambda: 'fantia user id:'+str(json_data['fanclub_user_id'])) \
 .values(lambda: 'creator:'+json_data['fanclub_user_name']) \
 .values(lambda: 'fantia id:'+str(json_data['post_id']))

g.urls(name = 'fantia URLs') \
 .values(lambda: json_data['post_url']) \
 .values(lambda: json_data['file_url'])

g.notes(name = 'fantia post/content comment', allowNoResult = True) \
 .values(lambda: assemble_note(json_data, 'fantia post comment', ['post_title'], ['comment'])) \
 .values(lambda: assemble_note(json_data, 'fantia content comment', ['content_tile'], ['content_comment']))
# endregion

#
# region: Fanbox
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/fanbox/'))

g.tags(name = 'fanbox generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'creator:'+json_data['creatorId']) \
 .values(lambda: 'fanbox id:'+json_data['id']) \
 .values(lambda: 'title:'+json_data['title']) \
 .values(lambda: 'creator:'+json_data['user']['name']) \
 .values(lambda: 'fanbox user id:'+json_data['user']['userId'])

g.tags(name = 'fanbox tags', tagRepos = defTagRepos, allowNoResult = True) \
 .values(lambda: json_data['tags'])

g.urls(name = 'fanbox URLs', allowEmpty = True) \
 .values(lambda: json_data['coverImageUrl'] if json_data['isCoverImage'] else '') \
 .values(lambda: json_data['fileUrl']) \
 .values(lambda: 'https://'+json_data['creatorId']+'.fanbox.cc/posts/'+json_data['id'])

g.notes(name = 'fanbox content') \
 .values(lambda: assemble_note(json_data, 'fanbox content', ['title'], ['content']))
# endregion

#
# region: lolibooru
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/lolibooru/'))

g.tags(name = 'lolibooru generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'lolibooru id:'+str(json_data['id'])) \
 .values(lambda: 'booru:lolibooru') \
 .values(lambda: 'rating:'+json_data['rating'])

g.tags(name = 'lolibooru tags', tagRepos = defTagRepos) \
 .values(lambda: map(lambda x: x.strip().replace('_', ' '),json_data['tags'].strip().split(' ')))

g.urls(name = 'lolibooru URLs', allowEmpty = True) \
 .values(lambda: json_data['file_url']) \
 .values(lambda: 'https://lolibooru.moe/post/show/'+str(json_data['id'])) \
 .values(lambda: json_data['source'])
# endregion

#
# region: yande.re
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/yandere/'))

g.tags(name = 'yandere generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'yandere id:'+str(json_data['id'])) \
 .values(lambda: 'booru:yande.re') \
 .values(lambda: 'rating:'+json_data['rating'])

g.tags(name = 'yandere tags', tagRepos = defTagRepos) \
 .values(lambda: map(lambda x: x.strip().replace('_', ' '),json_data['tags'].strip().split(' ')))

g.urls(name = 'yandere URLs', allowEmpty = True) \
 .values(lambda: json_data['file_url']) \
 .values(lambda: 'https://yande.re/post/show/'+str(json_data['id'])) \
 .values(lambda: json_data['source'])
# endregion

#
# region: Artstation
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/artstation/'))

g.tags(name = 'artstation generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'medium:'+json_data['medium']['name'] if json_data['medium'] else '') \
 .values(lambda: ['medium:'+med['name'] for med in json_data['mediums']]) \
 .values(lambda: ['software:'+soft['name'] for soft in json_data['software_items']]) \
 .values(lambda: ['artstation category:'+cat['name'] for cat in json_data['categories']]) \
 .values(lambda: ('creator:'+json_data['user']['full_name']) if json_data['user']['full_name'] else '') \
 .values(lambda: 'creator:'+json_data['user']['username']) \
 .values(lambda: 'title:'+json_data['title'])

g.tags(name = 'artstation tags', tagRepos = defTagRepos, allowNoResult = True) \
 .values(lambda: json_data['tags'])

g.urls(name = 'artstation asset image URL', allowEmpty = True) \
 .values(lambda: json_data['asset']['image_url'])

g.urls(name = 'artstation permalink', allowEmpty = True) \
 .values(lambda: json_data['permalink'])

g.notes(name = 'artstation description') \
 .values(lambda: assemble_note(json_data, 'artstation description', ['title'], ['description']))
# endregion

#
# region: imgur
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/imgur/'))

g.tags(name = 'imgur album title', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: ('title:'+json_data['album']['title']) if 'album' in json_data and json_data['album']['title'] else '')

g.tags(name = 'imgur title', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: ('title:'+json_data['title']) if json_data['title'] and json_data['title'].strip() else '')

g.urls(name = 'imgur image URL') \
 .values(lambda: json_data['url'])

g.urls(name = 'imgur album URL', allowEmpty = True) \
 .values(lambda: json_data['album']['url'] if 'album' in json_data else '')
# endregion

#
# region: seiso.party
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/seisoparty/'))

g.tags(name = 'seisoparty generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'title:'+json_data['title']) \
 .values(lambda: 'creator:'+json_data['username']) \
 .values(lambda: 'seiso.party service:'+json_data['service']) \
 .values(lambda: 'seiso.party id:'+json_data['id']) \
 .values(lambda: 'seiso.party user id:'+json_data['user'])
# endregion

#
# region: rule34.xxx
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/rule34/'))

g.tags(name = 'rule34 generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'rule34 id:'+json_data['id']) \
 .values(lambda: 'booru:rule34') \
 .values(lambda: 'rating:'+json_data['rating'])

def rule34_tags(jd):
    tags_from_namespaced_keys = [(key+':'+tag if key != 'general' else tag) for (key, tag) in get_namespaces_tags(jd, 'tags_')]
    if tags_from_namespaced_keys:
        return tags_from_namespaced_keys # the JSON contained tags_<namespace> keys. if present, those will have all the tags
    # otherwise try just "tags"
    if 'tags' in jd:
        return map(lambda x: x.strip().replace('_', ' '), jd['tags'].strip().split(' '))
    return []
ImportJob.f_rule34_tags = rule34_tags

g.tags(name = 'rule34 tags', tagRepos = defTagRepos, allowTagsEndingWithColon = True) \
 .values(lambda: ImportJob.f_rule34_tags(json_data))

g.urls(name = 'rule34 urls', allowEmpty = True) \
 .values(lambda: json_data['file_url']) \
 .values(lambda: 'https://rule34.xxx/index.php?page=post&s=view&id='+json_data['id']) \
 .values(lambda: json_data['source'])
# endregion

#
# region: e621
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/e621/'))

g.tags(name = 'e621 generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'e621 id:' + str(json_data['id'])) \
 .values(lambda: 'booru:e621') \
 .values(lambda: 'rating:' + json_data['rating'])

g.tags(name = 'e621 tags', tagRepos = defTagRepos, allowTagsEndingWithColon = True) \
 .values(lambda: get_nested_tags_e621(json_data['tags']))

g.tags(name = 'e621 post tags', tagRepos = defTagRepos, allowTagsEndingWithColon = True) \
 .values(lambda: get_nested_tags_e621(json_data['tags']))

g.urls(name = 'e621 urls', allowEmpty = True) \
 .values(lambda: json_data['gallerydl_file_url']) \
 .values(lambda: 'https://e621.net/posts/' + str(json_data['id']))
# endregion

#
# region: Furaffinity
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/furaffinity/'))

g.tags(name = 'furaffinity generated tags', tagRepos = defTagRepos, allowEmpty = True) \
 .values(lambda: 'furaffinity id:'+str(json_data['id'])) \
 .values(lambda: 'booru:furaffinity') \
 .values(lambda: 'rating:'+json_data['rating']) \
 .values(lambda: 'creator:'+json_data['artist']) \
 .values(lambda: 'title:'+json_data['title']) \
 .values(lambda: ('gender:'+json_data['gender']) if json_data['gender'] != 'Any' else '') \
 .values(lambda: ('species:'+json_data['species']) if json_data['species'] != 'Unspecified / Any' else '')

g.tags(name = 'furaffinity tags', tagRepos = defTagRepos, allowNoResult = True, allowEmpty = True, allowTagsEndingWithColon = True) \
 .values(lambda: [tag.replace('_', ' ') for tag in json_data['tags']])

g.urls(name = 'furaffinity urls', allowEmpty = True) \
 .values(lambda: json_data['url']) \
 .values(lambda: 'https://www.furaffinity.net/view/'+str(json_data['id'])+'/')
# endregion

#
# region: Instagram
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/instagram/'))

g.tags(name = 'instagram generated tags', tagRepos = defTagRepos, allowNoResult = True, allowEmpty = True, allowTagsEndingWithColon = True) \
 .values(lambda: 'creator:'+json_data['username']) \
 .values(lambda: 'name:'+json_data['fullname']) \
 .values(lambda: 'type:'+json_data['subcategory']) \
 .values(lambda: 'title:'+json_data['description']) \
 .values(lambda: 'instagram shortcode:'+json_data['shortcode']) \
 .values(lambda: 'source:'+str(json_data['category'])) \
 .values(lambda: 'page:'+str(json_data['num']) if json_data['count'] > 1 else '')

g.urls(name = 'instagram urls') \
 .values(lambda: 'https://www.instagram.com/p/'+str(json_data['shortcode']))
# endregion

#
# region: redgifs
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/redgifs/'))

g.tags(name = 'redgifs generated tags', tagRepos = defTagRepos, allowNoResult = True, allowEmpty = True) \
 .values(lambda: 'creator:'+json_data['userName']) \
 .values(lambda: 'redgifs id:'+json_data['filename']) \
 .values(lambda: 'source:'+str(json_data['category']))

g.tags(name = 'redgifs tags', tagRepos = defTagRepos, allowNoResult = True, allowEmpty = True, allowTagsEndingWithColon = True) \
 .values(lambda: [tag.replace('_', ' ') for tag in json_data['tags']])

g.urls(name = 'redgifs urls') \
 .values(lambda: 'https://www.redgifs.com/watch/'+str(json_data['filename']))
# endregion

#
# region: tiktok
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/tiktok/'))

g.tags(name = 'tiktok generated tags', tagRepos = defTagRepos, allowNoResult = True, allowEmpty = True) \
 .values(lambda: 'creator:'+json_data['author']['uniqueId']) \
 .values(lambda: 'name:'+json_data['author']['nickname']) \
 .values(lambda: 'tiktok id:'+str(json_data['id'])) \
 .values(lambda: 'source:'+str(json_data['category'])) \
 .values(lambda: 'title:'+json_data['title'])

g.urls(name = 'tiktok urls') \
 .values(lambda: 'https://www.tiktok.com/@'+str(json_data['author']['uniqueId'])+'/video/'+str(json_data['id']))
# endregion

#
# region: reddit
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/reddit/'))

g.tags(name = 'reddit generated tags', tagRepos = defTagRepos, allowNoResult = True, allowEmpty = True) \
 .values(lambda: 'subreddit:' + json_data['subreddit_name_prefixed'] if json_data.get('subreddit_type') != 'user' else '') \
 .values(lambda: 'creator:'+json_data['author']) \
 .values(lambda: 'reddit id:'+str(json_data['id'])) \
 .values(lambda: 'source:'+str(json_data['category'])) \
 .values(lambda: 'title:'+json_data['title']) \
 .values(lambda: 'site:reddit')

g.urls(name = 'reddit urls') \
 .values(lambda: 'https://www.reddit.com/'+str(json_data['permalink'])) \
 .values(lambda: 'https://i.redd.it/'+json_data['filename']+'.'+json_data['extension'])
# endregion

#
# region: Iwara
#

g = j.group(tagReposForNonUrlSources = defTagReposForNonUrlSources, filter = lambda: pstartswith(path, 'gallery-dl/iwara/'))

g.tags(name = 'iwara generated tags', tagRepos = defTagRepos) \
 .values(lambda: 'iwara id:'+json_data['id']) \
 .values(lambda: 'creator:'+json_data['user']['name']) \
 .values(lambda: 'creator:'+json_data['user']['nick']) \
 .values(lambda: 'title:'+json_data['title'])

g.notes(name = 'iwara post description', allowEmpty = True) \
 .values(lambda: "iwara post description\n"+str(json_data['user']['description']))
# endregion
