export const Scripts: ModdedBattleScriptsData = {
	inherit: 'gen9',
	gen: 9,
	init() {
    for (const id in this.data.Learnsets) {
      const learnsetEntry = this.data.Learnsets[id];
      const species = this.data.Pokedex[id];
      if (!learnsetEntry?.learnset || !species?.types) continue;
      learnsetEntry.learnset.essenceburst = ['9L1'];
      if (species.types.includes('Flying')) {
        learnsetEntry.learnset.clearingwinds = ['9L1'];
      }
      if (species.types.includes('Normal')) {
        learnsetEntry.learnset.escapeplan = ['9L1'];
      }
      if (species.types.includes('Steel')) {
        learnsetEntry.learnset.refine = ['9L1'];
      }
      if (species.types.includes('Dark')) {
        learnsetEntry.learnset.checkmate = ['9L1'];
      }
      if (species.types.includes('Fairy')) {
        learnsetEntry.learnset.irisgleam = ['9L1'];
      }
      if (species.types.includes('Ghost')) {
        learnsetEntry.learnset.eulogy = ['9L1'];
      }
      if (species.types.includes('Dragon')) {
        learnsetEntry.learnset.predation = ['9L1'];
      }
      if (species.types.includes('Ground')) {
        learnsetEntry.learnset.faultline = ['9L1'];
      }
      if (species.types.includes('Fire')) {
        learnsetEntry.learnset.evaporate = ['9L1'];
      }
      if (species.types.includes('Water')) {
        learnsetEntry.learnset.lather = ['9L1'];
      }
      if (species.types.includes('Electric')) {
        learnsetEntry.learnset.shortcircuit = ['9L1'];
      }
      if (species.types.includes('Grass')) {
        learnsetEntry.learnset.foulfoliage = ['9L1'];
      }
      if (species.types.includes('Ice')) {
        learnsetEntry.learnset.icebreaker = ['9L1'];
      }
      if (species.types.includes('Poison')) {
        learnsetEntry.learnset.sludgetrap = ['9L1'];
      }
      if (species.types.includes('Bug')) {
        learnsetEntry.learnset.silkenshroud = ['9L1'];
      }
      if (species.types.includes('Rock')) {
        learnsetEntry.learnset.rockfall = ['9L1'];
      }
      if (species.types.includes('Psychic')) {
        learnsetEntry.learnset.telekinetictoss = ['9L1'];
      }
      if (species.types.includes('Fighting')) {
        learnsetEntry.learnset.overwhelm = ['9L1'];
      }
      if (species.types.includes('Light')) {
        learnsetEntry.learnset.exposure = ['9L1'];
      }
      if (species.types.includes('Cosmic')) {
        learnsetEntry.learnset.terraformbeam = ['9L1'];
      }
    }
    
  },
};
