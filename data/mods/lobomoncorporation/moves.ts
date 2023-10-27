export const Moves: {[k: string]: ModdedMove Data} = {
  freezingkiss:{
    num: 0,
    accuracy: 50,
    basePower: 0,
    category: "Status",
    name: "Freezing Kiss",
    pp: 10,
    priority: 0,
    flags: {protect:1, reflectable: 1, mirror: 1},
    status: 'frz',
    secondary: null,
    target: "normal",
    type: "Ice",
    zMove: {boost: {spa: 1}},
    contestType: "Beautiful",
  },
}
