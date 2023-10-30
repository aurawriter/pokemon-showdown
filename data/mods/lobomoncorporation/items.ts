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
	   desc: "At the end of every turn, this item attempts to burn the holder.",
	},
};
