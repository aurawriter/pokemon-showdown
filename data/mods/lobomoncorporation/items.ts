export const Items: {[k: string]: ModdedItemData} = {
  frostorb: {
		name: "Frost Orb",
		spritenum: 145,
		fling: {
			basePower: 30,
			status: 'fbt',
		},
		onResidualOrder: 28,
		onResidualSubOrder: 3,
		onResidual(pokemon) {
			pokemon.trySetStatus('fbt', pokemon);
		},
		num: 273,
	},
};
