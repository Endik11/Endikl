class DamageScaling:
    TABLE=(1.0,.95,.88,.80,.72,.65,.58,.50)
    @classmethod
    def factor(cls,hit_count,minimum=.40): return max(minimum,cls.TABLE[min(max(hit_count-1,0),len(cls.TABLE)-1)])
    @classmethod
    def damage(cls,base,hit_count,defense=1.0,modifier=1.0,minimum_damage=1,minimum_scaling=.40): return max(minimum_damage,round(base*cls.factor(hit_count,minimum_scaling)*modifier/max(.01,defense)))
