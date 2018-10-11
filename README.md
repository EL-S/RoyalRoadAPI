# RoyalRoadLAPI
A Python API to request data from the fanfiction website RoyalRoadL

To obtain data from a fiction, you must first call the get_fiction_object() function.
get_fiction_object() takes a single argument, the fiction id, and returns a parsed html file of the fiction page.

With this object, you can request data from the page without making a http request for each piece of data.

eg.

  fiction = get_fiction_object(a_fiction_id) # to get the fiction page
  title = get_fiction_title(fiction) # to get the fictions title

Data that can be requested includes:

get_fiction_title(fiction)
  returns the title as a string
get_fiction_cover_image(fiction)
  returns the webaddress of the cover image for the fiction as string
get_fiction_author(fiction)
  returns the author as a string
get_fiction_description(fiction)
  returns the fiction description as a string
get_fiction_genres(fiction)
  returns all the genres as a list
get_fiction_rating(fiction)
  returns all the different ratings as a list [overall_rating,best_rating,rating_count,style_rating,story_rating,character_rating,grammar_rating]
get_fiction_statistics(fiction)
  returns the fictions statistics as a list [total_views,average_views,followers,favorites,pages]
get_chapter_links(fiction)
  returns the links to each chapter of the fiction as a list, in original chronological order
get_chapter_amount(fiction) #or simply get the length of the list returned above
  returns the amount of chapters as an integer, reccommended to get the length of chapter_link instead if both are needed (to be efficient)
