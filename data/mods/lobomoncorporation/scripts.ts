export const Scripts: ModdedBattleScriptsData = {
	gen: 9,
	inherit: 'gen9',
	actions:{
		modifyDamage(baseDamage,pokemon,target,move,suppressMessages){
			if (pokemon.status === 'brn' && move.category === 'Physical' && !pokemon.hasAbility('guts')) {
				if (move.id !== 'facade' || move.id !== 'shadowpunch') {
					baseDamage = this.battle.modify(baseDamage, 0.5);
					}
			if (pokemon.status === 'fbt' && move.category === 'Special')){
				if(move.id!=='facade'){
					baseDamage = this.battle.modify(baseDamage,0.5);
					}
				}
			}
		}
	},
};
