# this is example on how to code custom patterns for rwe+ tile editor
# custom code pattens use python

if destroy: # if we destroying instead of placing
	#sam could be achieved by using self.tool == 1 because 1 is destroy(0 - place, 1 - destroy, 2 - copy)

	# use mornaldestroy function remove use normal destroy whenever we use destroy
	normaldestroy(destroy)
# first off, we need to decide if we use rect tool or pen(brush is not working rn)
elif userect: # userect checks if we use rect to fill
	# this block executes after we selecterd an area with rect(after we pressed rmb)
	# position of our cursor is rect.bottomright or just [rect.x + rect.w, rect.y + rect.h]

	# normal rect procedure, iterating over all pixels in our rect
	# it's important to add int() because pg.Rect.x and y returns float
	for y in range(int(rect.h)):
		for x in range(int(rect.w)):
			# checking if our tile will be placed near rect border(just to teach you about these conditions)
			if x == 0 or y == 0 or x == rect.w - 1 or y == rect.h - 1:
				# setting tile without rendering it
				# using savedtile["conf"] to acces things we saved in patterns.json
				# we don't need to change dorecreate argument since we set render to false here   VV
				self.set(savedtile["conf"]["examplecat"], savedtile["conf"]["examplenameborder"], False)
			else: # if tile inside of border
				self.set(savedtile["conf"]["examplecat"], savedtile["conf"]["examplename"], False)

			# to get x and y pos on field, use x + rext.x and y + rect.y
			# placing tile with self.place without rendering it
			self.place(rect.x + x, rect.y + y)
else:
	# this block executes when we use pen(or just lmb)

	# setting our tile with render as true, but do not change window title
	self.set(savedtile["conf"]["examplecat"], savedtile["conf"]["examplename"], True, dorecaption=False)
	
	# position of our cursor is rect.topleft or just [rect.x, rect.y]
	# placing tile with save.place and rendering it on viewport
	self.place(rect.x, rect.y, True)
# anything else after


# helpful info
# before first pattern code executes, you save your current pattern and after pattern executes all scripts you select saved patten back
# you can access it as savedtile
# to use any of pygame's stuff, use pg

# DON'T EVER MODIFY self.data BY YOURESELF OR MATTER OF THE UNIVERSE WOULD BREAK
# instead use self.changedata(path_to_data, value_to_change, check_if_value_didnt_change)
# example: self.changedata(["GE", 5, 12, 1, 0], 1, True) will change data of geo on position [5, 12] on layer 2 to 1 and wouldn't change if it's same

# to access level geometry, use self.data["GE"][x][y][layer] or just self.data.GE_data(x, y, layer)
# simillar to geometry, use self.data["TE"]["tlMatrix"][x][y][layer] or just self.data.TE_data(x, y, layer)
# for more info, use https://docs.google.com/document/d/1zcxeQGibkZORstwGQUovhQk71k00B69oYwkqFpGyOqs/edit

# you can get any tile data you want with self.tiles
# to get tile by name use self.tiles[name] (name is string)
# to get tile by name and category, use self.tiles[category, name] (category and name are strings)
# to get category, use self.tiles[category] (category should be int)
# 	to get this category's item list, use self.tiles[category]["items"]
# 	to get this category's name, use self.tiles[category]["name"]

# use self.set to set current placing tile
# self.set arguments
# 1. cat: string            - category of tile as string
# 2. name: string           - name of tile as string
# 3. render: bool=True      - render and resize tile on select. should be used when we would draw tile as preview(aka when we don't use rect)
# 4. usefavs: bool=False    - (obsolete for patterns)use tiles from favourites. should remain False
# 5. dorecaption: bool=True - (always false for pattens)change window title if true AND render is true. should be set to false when we don't want for tile name to be shown(aka always)

# use self.place to place tiles you set on current layer
# self.place arguments
# 1. x: int, float      - x pos of placed tile(from top left corner)
# 2. y: int, float      - y pos of placed tile(from top left corner)
# 3. render: bool=False - render tile preview when placed. if true, self.set before also should have render as true. shouldn't be used when using rect

# use self.destroy to remove tiles in spot on current layer(what part of tile will be deleted doesn't matter since it delets all of tile)
# self.destroy arguments
# 1. xp: int, float             - x position of tile that should be deleted
# 2. yp: int, float             - y position of tile that should be deleted
# 3. render: bool=True          - should it render rect of chosen color on space of tile
# 4. destroycolor: pg.Color=red - color of rect(obsolete if render is false)

# use self.test_cols to check if you can place set tile in specific position
# self.test_cols arguments
# 1. x: int, float - x position of tile
# 2. y: int, float - y position of tile
# returns true if tile can be placed without any problems(also checks if force geo or force place keys pressed)

# use self.gettile to check what tile is placed on specific spot
# returns None if placed on material or there's no tile
# else returns tile item with all the parameters and images
# self.gettile arguments
# 1. x: int, float - x position of tile
# 2. y: int, float - y position of tile
# returns tile as item(aka dict) with frequently used ones as:
# "nm" - name of tile
# "category" - category of tile
# "description" - tile description
# "tags" - list of tags
# "cols" - list of 2 other lists with collisions
# "color" - color of category tile in
# "image" - tile preview image
# "bfTiles" - buffer tiles(check some tile creating tutorials)
# "size" - size of tile(width and height)