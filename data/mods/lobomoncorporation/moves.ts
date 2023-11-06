export const Moves: {[k: string]: ModdedMoveData} = {
  freezingkiss: {
    num: 0,
    accuracy: 85,
    basePower: 0,
    category: "Status",
	 desc: "Inflicts frostbite on the target",
    shortDesc: "Frostbites the target",
    name: "Freezing Kiss",
    pp: 15,
    priority: 0,
    flags: {protect:1, reflectable: 1, mirror: 1},
    status: 'fbt',
    secondary: null,
    target: "normal",
    type: "Ice",
    zMove: {boost: {spa: 1}},
    contestType: "Beautiful",
  },
	blizzard: {
		inherit: true,
		secondary: {
			chance: 30,
			status: 'fbt',
		},
		desc: "30% chance to frostbite foe(s). Can't miss in Snow.",
		shortDesc: "30% chance to frostbite foe(s). Can't miss in Snow.",
	},
	freezedry: {
		inherit: true,
		secondary:{
			chance: 10,
			status: 'fbt',
		},
		desc: "10% chance to frostbite. Super effective on Water.",
		shortDesc: "10% chance to frostbite. Super effective on Water."
	},
	freezingglare: {
		inherit: true,
		secondary: {
			chance: 10,
			status: 'fbt',
		},
		desc: "10% chance to frostbite the target.",
		shortDesc: "10% chance to frostbite the target.",
	},
	icebeam: {
		inherit: true,
		secondary: {
			chance: 10,
			status: 'fbt',
		},
		desc: "10% chance to frostbite the target.",
		shortDesc: "10% chance to frostbite the target.",
	},
	icefang: {
		inherit: true,
		secondaries: [
			{
				chance: 10,
				status: 'fbt',
			}, {
				chance: 10,
				volatileStatus: 'flinch',
			},
		],
		desc: "10% chance to frostbite. 10% chance to flinch.",
		shortDesc: "10% chance to frostbite. 10% chance to flinch",
	},
	icepunch: {
		inherit: true,
		secondary: {
			chance: 10,
			status: 'fbt',
		},
		desc: "10% chance to frostbite the target.",
		shortDesc: "10% chance to frostbite the target.",
	},
	powdersnow: {
		inherit: true,
		secondary: {
			chance: 10,
			status: 'fbt',
		},
		desc: "10% chance to frostbite foe(s)",
		shortDesc: "10% chance to frostbite foe(s)",
	},
	triattack: {
		inherit: true,
		secondary: {
			chance: 20,
			onHit(target, source) {
				const result = this.random(3);
				if (result === 0) {
					target.trySetStatus('brn', source);
				} else if (result === 1) {
					target.trySetStatus('par', source);
				} else {
					target.trySetStatus('fbt', source);
				}
			},
		},
		desc: "20% chance to paralyze or burn or frostbite target.",
		shortDesc: "20% chance to paralyze or burn or frostbite target.",
	},
	wobble: {
		num: 150,
		accuracy: true,
		basePower: 0,
		category: "Status",
		name: "Wobble",
		pp: 40,
		priority: 0,
		flags: {gravity: 1},
		onTry(source, target, move) {
			// Additional Gravity check for Z-move variant
			if (this.field.getPseudoWeather('Gravity')) {
				this.add('cant', source, 'move: Gravity', move);
				return null;
			}
		},
		onTryHit(target, source) {
			this.add('-nothing');
		},
		secondary: null,
		target: "self",
		type: "Normal",
		zMove: {boost: {atk: 3}},
		contestType: "Cute",
		desc: "Only good for training",
		shortDesc: "Only good for training",
	},
	timebomb: {
		num: 248,
		accuracy: 100,
		basePower: 120,
		category: "Physical",
		name: "Time Bomb",
		desc: "In 3 turns, the opposing side takes Fire-damage",
		shortDesc: "In 3 turns deal Fire-type damage",
		pp: 10,
		priority: 0,
		flags: {allyanim: 1, futuremove: 1},
		ignoreImmunity: true,
		onTry(source, target) {
			if (!target.side.addSlotCondition(target, 'futuremove')) return false;
			Object.assign(target.side.slotConditions[target.position]['futuremove'], {
				duration: 3,
				move: 'timebomb',
				source: source,
				moveData: {
					id: 'timebomb',
					name: "Time Bomb",
					accuracy: 100,
					basePower: 120,
					category: "Physical",
					priority: 0,
					flags: {allyanim: 1, futuremove: 1},
					ignoreImmunity: false,
					effectType: 'Move',
					type: 'Fire',
				},
			});
			this.add('-start', source, 'move: Future Sight');
			return this.NOT_FAIL;
		},
		secondary: null,
		target: "normal",
		type: "Fire",
		contestType: "Clever",
	},
	cleansing: {
		num: 499,
		accuracy: true,
		basePower: 50,
		category: "Special",
		desc: "Cleanses the target, dealing supereffective damage to Ghosts and removing stat boosts.",
   	shortDesc: "Removes stat boosts and deals super-effective damage to Ghosts.",
		name: "Cleansing",
		pp: 15,
		priority: 0,
		flags: {protect: 1, mirror: 1},
		onEffectiveness(typeMod, target, type, move) {
           if (move.type !== 'Normal') return;
			  if (!target) return;
			  if(!target.runImmunity('Normal')){
			  		if(target.hasType('Ghost')) return 1;
			  }
			  //if(type==='Ghost') return 1;
        },
		onHit(target) {
			target.clearBoosts();
			this.add('-clearboost', target);
		},
		ignoreImmunity: {'Normal': true},
		secondary: null,
		target: "normal",
		type: "Normal",
		contestType: "Beautiful",
	},
	solitude: {
		num: 609,
		accuracy: 100,
		basePower: 20,
		category: "Special",
		name: "Solitude",
		pp: 20,
		priority: 0,
		flags: {protect: 1, mirror: 1},
		secondary: {
			chance: 100,
			status: 'dsp',
		},
		target: "normal",
		type: "Psychic",
		contestType: "Beautiful",
		shortDesc: "Fills the target with despair",
	},
	bearhug: {
		num: 83,
		accuracy: 85,
		basePower: 35,
		category: "Physical",
		name: "Bear Hug",
		pp: 15,
		priority: 0,
		flags: {contact: 1, protect: 1, mirror: 1},
		volatileStatus: 'partiallytrapped',
		secondary: null,
		target: "normal",
		type: "Fighting",
		contestType: "Beautiful",
		desc: "Happy Teddy Bear doesn't want to let go",
		shortDesc: "Traps and damages the target for 4-5 turns."
	},
	arcanabeats: {
		num: 295,
		accuracy: 100,
		basePower: 70,
		category: "Special",
		name: "Arcana Beats",
		desc: "50% to reduce Sp. Defense",
		pp: 10,
		priority: 0,
		flags: {protect: 1, mirror: 1},
		secondary: {
			chance: 50,
			boosts: {
				spd: -1,
			},
		},
		target: "normal",
		type: "Fairy",
		contestType: "Clever",
		shortDesc: "50% chance to reduce Sp. Def.",
	},
	arcanaslave: {
		num: 553,
		accuracy: 90,
		basePower: 120,
		category: "Physical",
		name: "Arcana Slave",
		desc: "70% to reduce Sp. Defense",
		shortDesc: "70% chance to reduce Sp. Def.",
		pp: 10,
		priority: 0,
		flags: {protect: 1, mirror: 1, nosleeptalk: 1, failinstruct: 1},
		secondary: {
			chance: 50,
			boosts: {
				spd: -2,
			},
		},
		target: "normal",
		type: "Fairy",
		contestType: "Beautiful",
	},
hearttaker: {
		num: 893,
		accuracy: 100,
		basePower: 160,
		category: "Physical",
		name: "Hearttaker",
	   desc: "Cannot be used twice in a row.",
	   shortDesc: "Cannot be used twice in a row.",
		pp: 5,
		priority: 0,
		flags: {protect: 1, mirror: 1},
		onDisableMove(pokemon) {
			if (pokemon.lastMove?.id === 'hearttaker') pokemon.disableMove('hearttaker');
		},
		beforeMoveCallback(pokemon) {
			if (pokemon.lastMove?.id === 'hearttaker') pokemon.addVolatile('hearttaker');
		},
		onAfterMove(pokemon) {
			if (pokemon.removeVolatile('hearttaker')) {
				this.add('-hint', "Some effects can force a Pokemon to use Hearttaker again in a row.");
			}
		},
		condition: {},
		secondary: null,
		target: "normal",
		type: "Steel",
	},
	enchantingflame: {
		num: 503,
		accuracy: 100,
		basePower: 80,
		category: "Special",
		name: "Enchanting Flame",
		pp: 15,
		priority: 0,
		flags: {protect: 1, mirror: 1, defrost: 1},
		thawsTarget: true,
		secondary: {
			chance: 30,
			status: 'par',
		},
		target: "normal",
		type: "Fire",
		contestType: "Tough",
		desc: "30% chance of paralysis",
		shortDesc: "30% chance of paralysis",
	},
	spinningblade: {
		num: 899,
		accuracy: 100,
		basePower: 100,
		category: "Physical",
		name: "Spinning Blade",
		pp: 10,
		priority: 0,
		flags: {
			protect: 1, failencore: 1, failmefirst: 1, nosleeptalk: 1, noassist: 1, failcopycat: 1, failinstruct: 1, failmimic: 1,
		},
		target: "normal",
		type: "Steel",
		desc: "No additional effect",
		shortDesc: "No additional effect",
	},
	tangledbramble: {
		num: 446,
		accuracy: true,
		basePower: 0,
		category: "Status",
		name: "Tangled Bramble",
		pp: 20,
		priority: 0,
		flags: {reflectable: 1, mustpressure: 1},
		sideCondition: 'tangledbramble',
		condition: {
			// this is a side condition
			onSideStart(side) {
				this.add('-sidestart', side, 'move: Tangled Bramble');
			},
			onEntryHazard(pokemon) {
				if (pokemon.hasItem('heavydutyboots')) return;
				const typeMod = this.clampIntRange(pokemon.runEffectiveness(this.dex.getActiveMove('tangledbramble')), -6, 6);
				this.damage(pokemon.maxhp * Math.pow(2, typeMod) / 8);
			},
		},
		secondary: null,
		target: "foeSide",
		type: "Grass",
		zMove: {boost: {def: 1}},
		contestType: "Cool",
		desc: "Hurts foes on switch-in. Factors Grass weakness.",
		shortDesc: "Hurts foes on switch-in. Factors Grass weakness",
	},
	crimsonshot: {
		num: 179,
		accuracy: 100,
		basePower: 0,
		basePowerCallback(pokemon, target) {
			const ratio = Math.max(Math.floor(pokemon.hp * 48 / pokemon.maxhp), 1);
			let bp;
			if (ratio < 2) {
				bp = 200;
			} else if (ratio < 5) {
				bp = 150;
			} else if (ratio < 10) {
				bp = 100;
			} else if (ratio < 17) {
				bp = 80;
			} else if (ratio < 33) {
				bp = 40;
			} else {
				bp = 20;
			}
			this.debug('BP: ' + bp);
			return bp;
		},
		category: "Special",
		name: "Crimson Shot",
		pp: 15,
		priority: 0,
		flags: {protect: 1, mirror: 1},
		secondary: null,
		target: "normal",
		type: "Dark",
		zMove: {basePower: 160},
		contestType: "Cool",
		desc: "More power the less HP the user has left.",
		shortDesc: "More power the less HP the user has left.",
	},
	pitchblack: {
		num: 240,
		accuracy: true,
		basePower: 0,
		category: "Status",
		name: "Pitch Black",
		pp: 5,
		priority: 0,
		flags: {},
		weather: 'PitchBlack',
		secondary: null,
		target: "all",
		type: "Dark",
		zMove: {boost: {spe: 1}},
		contestType: "Beautiful",
		shortDesc: "For 5 turns, power super-effective moves and weaken Psychic moves",
		desc: "For 5 turns, darkness strengthens super-effective moves, and weaknes Psychic moves",
	},
	swarmstrike: {
		num: 534,
		accuracy: 100,
		basePower: 80,
		category: "Physical",
		name: "Swarm Strike",
		pp: 10,
		priority: 0,
		flags: {contact: 1, protect: 1, mirror: 1, slicing: 1},
		secondary: {
			chance: 30,
			boosts: {
				def: -1,
			},
		},
		target: "normal",
		type: "Bug",
		contestType: "Cool",
		desc: "30% chance to reduce Defense",
		shortDesc: "30% chance to reduce Defense",
	},
	grasswhistle: {
		inherit: true,
		status: 'dzy',
		accuracy: 90,
	},
	hypnosis: {
		inherit: true,
		status: 'dzy',
		accuracy: 90,
	},
	lovelykiss: {
		inherit: true,
		status: 'dzy',
		accuracy: 90,
	},
	sing: {
		inherit: true,
		status: 'dzy',
		accuracy: 90,
	},
	sleeppowder: {
		inherit: true,
		status: 'dzy',
		accuracy: 90,
	},
	direclaw: {
		inherit: true,
		secondary: {
			chance: 50,
			onHit(target, source) {
				const result = this.random(3);
				if (result === 0) {
					target.trySetStatus('psn', source);
				} else if (result === 1) {
					target.trySetStatus('par', source);
				} else {
					target.trySetStatus('dzy', source);
				}
			},
		},
	},
	
};
