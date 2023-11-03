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
	},
	freezedry: {
		inherit: true,
		secondary:{
			chance: 30,
			status: 'fbt',
		}
	},
	freezingglare: {
		inherit: true,
		secondary: {
			chance: 30,
			status: 'fbt',
		},
	},
	icebeam: {
		inherit: true,
		secondary: {
			chance: 30,
			status: 'fbt',
		},
	},
	icefang: {
		inherit: true,
		secondaries: [
			{
				chance: 30,
				status: 'fbt',
			}, {
				chance: 10,
				volatileStatus: 'flinch',
			},
		],
	},
	icepunch: {
		inherit: true,
		secondary: {
			chance: 30,
			status: 'fbt',
		},
	},
	powdersnow: {
		inherit: true,
		secondary: {
			chance: 30,
			status: 'fbt',
		},
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
	},
	arcanabeats: {
		num: 295,
		accuracy: 100,
		basePower: 70,
		category: "Special",
		name: "Arcana Beats",
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
	},
	arcanaslave: {
		num: 553,
		accuracy: 90,
		basePower: 120,
		category: "Physical",
		name: "Arcana Slave",
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
		pp: 5,
		priority: 0,
		flags: {protect: 1, mirror: 1},
		onDisableMove(pokemon) {
			if (pokemon.lastMove?.id === 'gigatonhammer') pokemon.disableMove('gigatonhammer');
		},
		beforeMoveCallback(pokemon) {
			if (pokemon.lastMove?.id === 'gigatonhammer') pokemon.addVolatile('gigatonhammer');
		},
		onAfterMove(pokemon) {
			if (pokemon.removeVolatile('gigatonhammer')) {
				this.add('-hint', "Some effects can force a Pokemon to use Gigaton Hammer again in a row.");
			}
		},
		condition: {},
		secondary: null,
		target: "normal",
		type: "Steel",
	},
};
