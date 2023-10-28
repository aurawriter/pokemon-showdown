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
	}
};
