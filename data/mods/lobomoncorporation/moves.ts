export const Moves: {[k: string]: ModdedMoveData} = {
  freezingkiss:{
    num: 0,
    accuracy: 85,
    basePower: 0,
    category: "Status",
	 desc: "Inflicts frostbite on the target",
    shortdesc: "Frostbites the target",
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
	blizzard:{
		inherit: true,
		secondary: {
			chance: 30,
			status: 'fbt',
		},
	},
	freezedry:{
		inherit: true,
		secondary:{
			chance: 30,
			status: 'fbt',
		}
	},
	freezingglare:{
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
	icefang:{
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
	powdersnow:{
		inherit: true,
		secondary: {
			chance: 30,
			status: 'fbt',
		},
	},
	triattack:{
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
	},
	timebomb: {
		num: 248,
		accuracy: 100,
		basePower: 120,
		category: "Physical",
		name: "Time Bomb",
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
};
