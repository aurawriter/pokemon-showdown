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
	theresia: {
		name: "Theresia",
		desc: "At the end of every turn, holder restores 1/16 of its max HP.",
		spritenum: 242,
		fling: {
			basePower: 10,
		},
		onResidualOrder: 5,
		onResidualSubOrder: 4,
		onResidual(pokemon) {
			this.heal(pokemon.baseMaxhp / 8);
			pokemon.trySetStatus('dsp', pokemon);
		},
		num: 234,
		heal: "Theresia's song soothed [POKEMON].",
	},
	mimickry: {
		name: "Mimickry",
		spritenum: 438,
		fling: {
			basePower: 30,
		},
		onAfterMoveSecondarySelfPriority: -1,
		onAfterMoveSecondarySelf(pokemon, target, move) {
			if (move.totalDamage && !pokemon.forceSwitchFlag) {
				this.heal(move.totalDamage / 8, pokemon);
			}
		},
		num: 253,
		desc: "After an attack, holder gains 1/8 of the damage in HP dealt to other Pokemon.",

		heal: "  [POKEMON] restored a little HP using its Shell Bell!",
	},
};
