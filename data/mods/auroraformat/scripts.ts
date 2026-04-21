export const Scripts: ModdedBattleScriptsData = {
	inherit: 'gen9',
	gen: 9,
	init() {
    for (const id in this.data.Learnsets) {
      const learnsetEntry = this.data.Learnsets[id];
      const species = this.data.Pokedex[id];
      if (!learnsetEntry?.learnset || !species?.types) continue;
      const isArceus = species.name.startsWith('Arceus');
      const isSilvally = species.name.startsWith('Silvally');
      const isRotom = species.name.startsWith('Rotom');
      learnsetEntry.learnset.essenceburst = ['9L1'];
      if (species.types.includes('Flying') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.clearingwinds = ['9L1'];
      }
      if (species.types.includes('Normal') && !isRotom) {
        learnsetEntry.learnset.escapeplan = ['9L1'];
      }
      if (species.types.includes('Steel') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.refine = ['9L1'];
      }
      if (species.types.includes('Dark') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.checkmate = ['9L1'];
      }
      if (species.types.includes('Fairy') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.irisgleam = ['9L1'];
      }
      if (species.types.includes('Ghost') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.eulogy = ['9L1'];
      }
      if (species.types.includes('Dragon') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.predation = ['9L1'];
      }
      if (species.types.includes('Ground') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.faultline = ['9L1'];
      }
      if (species.types.includes('Fire') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.evaporate = ['9L1'];
      }
      if (species.types.includes('Water') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.lather = ['9L1'];
      }
      if (species.types.includes('Electric') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.shortcircuit = ['9L1'];
      }
      if (species.types.includes('Grass') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.foulfoliage = ['9L1'];
      }
      if (species.types.includes('Ice') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.icebreaker = ['9L1'];
      }
      if (species.types.includes('Poison') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.sludgetrap = ['9L1'];
      }
      if (species.types.includes('Bug') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.silkenshroud = ['9L1'];
      }
      if (species.types.includes('Rock') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.rockfall = ['9L1'];
      }
      if (species.types.includes('Psychic') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.telekinetictoss = ['9L1'];
      }
      if (species.types.includes('Fighting') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.overwhelm = ['9L1'];
      }
      if (species.types.includes('Light') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.exposure = ['9L1'];
      }
      if (species.types.includes('Cosmic') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.terraformbeam = ['9L1'];
      }
    }
    
  },
};
