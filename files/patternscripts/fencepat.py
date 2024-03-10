if destroy:
	normaldestroy(destroy)
elif userect:
	for y in range(int(rect.h)):
		for x in range(int(rect.w)):
			pole = "_pole" if x % savedtile["conf"]["offsetx"] == 0 else ""
			if y < savedtile["conf"]["offsety"]:
				self.set(savedtile["conf"]["searchcat"], savedtile["conf"]["wire" + pole], False)
			elif y == savedtile["conf"]["offsety"]:
				self.set(savedtile["conf"]["searchcat"], savedtile["conf"]["fence_end" + pole], False)
			else:
				self.set(savedtile["conf"]["searchcat"], savedtile["conf"]["fence" + pole], False)
			self.place(x + rect.x, y + rect.y)
else:
	self.set(savedtile["conf"]["searchcat"], savedtile["conf"]["fence"], dorecaption=False)
	self.place(rect.x, rect.y, True)