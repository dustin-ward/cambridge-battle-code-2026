

def run_sentinel(self):
    for id in self.c.get_nearby_entities():
        if self.c.get_team() != self.c.get_team(id):
            pos = self.c.get_position(id)
            print(f'enemy spotted: {pos}')
            if self.c.can_fire(pos):
                self.c.fire(pos)
            else:
                print('couldn\'t fire')
