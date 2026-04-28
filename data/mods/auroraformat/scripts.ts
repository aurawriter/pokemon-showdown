export const Scripts: ModdedBattleScriptsData = {
	inherit: 'gen9',
	gen: 9,
	init() {
    for (const id in this.data.Learnsets) {
      const learnsetEntry = this.data.Learnsets[id];
      const species = this.data.Pokedex[id];
      if (!learnsetEntry?.learnset || !species?.types) continue;
      delete learnsetEntry.learnset.terablast;
      const isArceus = species.name.startsWith('Arceus');
      const isSilvally = species.name.startsWith('Silvally');
      const isRotom = species.name.startsWith('Rotom');
      const isGiftrap = species.name.startsWith('Giftrap');
      const isMagikarp = species.name.startsWith('Magikarp');
      const isDitto = species.name.startsWith('Ditto');
      const isNincada = species.name.startsWith('Nincada');
      if (!isMagikarp && !isDitto) 
      {
      learnsetEntry.learnset.essenceburst = ['9M'];
      }
      if (species.types.includes('Flying') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.clearingwinds = ['9M'];
      }
      if (species.types.includes('Normal') && !isDitto) {
        learnsetEntry.learnset.escapeplan = ['9M'];
      }
      if (species.types.includes('Steel') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.refine = ['9M'];
      }
      if (species.types.includes('Dark') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.checkmate = ['9M'];
      }
      if (species.types.includes('Fairy') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.irisgleam = ['9M'];
      }
      if (species.types.includes('Ghost') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.eulogy = ['9M'];
      }
      if (species.types.includes('Dragon') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.predation = ['9M'];
      }
      if (species.types.includes('Ground') && !isSilvally && !isArceus && !isNincada) {
        learnsetEntry.learnset.faultline = ['9M'];
      }
      if (species.types.includes('Fire') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.evaporate = ['9M'];
      }
      if (species.types.includes('Water') && !isSilvally && !isArceus && !isRotom&& !isMagikarp) {
        learnsetEntry.learnset.lather = ['9M'];
      }
      if (species.types.includes('Electric') && !isSilvally && !isArceus && !isGiftrap) {
        learnsetEntry.learnset.shortcircuit = ['9M'];
      }
      if (species.types.includes('Grass') && !isSilvally && !isArceus && !isRotom) {
        learnsetEntry.learnset.foulfoliage = ['9M'];
      }
      if (species.types.includes('Ice') && !isSilvally && !isArceus && !isRotom && !isGiftrap) {
        learnsetEntry.learnset.icebreaker = ['9M'];
      }
      if (species.types.includes('Poison') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.sludgetrap = ['9M'];
      }
      if (species.types.includes('Bug') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.deafeningthrum = ['9M'];
      }
      if (species.types.includes('Rock') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.rockfall = ['9M'];
      }
      if (species.types.includes('Psychic') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.telekinetictoss = ['9M'];
      }
      if (species.types.includes('Fighting') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.overwhelm = ['9M'];
      }
      if (species.types.includes('Light') && !isSilvally && !isArceus && !isGiftrap) {
        learnsetEntry.learnset.exposure = ['9M'];
      }
      if (species.types.includes('Cosmic') && !isSilvally && !isArceus) {
        learnsetEntry.learnset.terraformbeam = ['9M'];
      }
    }
    
  },
};
