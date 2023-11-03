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
	   desc: "At the end of every turn, this item attempts to frostbite the holder.",
	},
	redshoes: {
		name: "Red Shoes",
		spritenum: 249,
		fling: {
			basePower: 30,
		},
		onModifyDamage(damage, source, target, move) {
			return this.chainModify([5324, 4096]);
		},
		onAfterMoveSecondarySelf(source, target, move) {
			if (source && source !== target && move && move.category !== 'Status' && !source.forceSwitchFlag) {
				this.damage(source.baseMaxhp / 10, source, source, this.dex.items.get('lifeorb'));
			}
		},
		num: 270,
		desc: "Holder's attacks do 1.3x damage, and it loses 1/10 its max HP after the attack.",
		damage: "The shoes bit [POKEMON]!",
	},
};
