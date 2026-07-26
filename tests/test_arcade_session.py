from game.modes.arcade_session import ArcadeSession


FIGHTERS=["kael","sable","orrin","mira","lin","ren_kaido"]


def test_ladder_is_deterministic_valid_and_excludes_player():
    a=ArcadeSession.create("kael",FIGHTERS,42);b=ArcadeSession.create("kael",FIGHTERS,42)
    assert a.opponents==b.opponents and len(a.opponents)>=4 and "kael" not in a.opponents
    assert all(x!=y for x,y in zip(a.opponents,a.opponents[1:]))


def test_progress_difficulty_continue_and_reward_are_idempotent():
    session=ArcadeSession.create("kael",FIGHTERS,2,"easy");levels=[]
    for index in range(len(session.opponents)):
        levels.append(session.current_difficulty);assert session.record_result(f"r{index}",True)
    assert session.completed and session.rewards==["arcade_complete"] and not session.record_result("r0",True)
    assert levels[0]=="easy" and levels[-1] in {"medium","hard"}
    failed=ArcadeSession.create("sable",FIGHTERS,3);failed.record_result("loss",False);assert failed.use_continue()


def test_save_restore_and_corrupt_ladder_fallback():
    session=ArcadeSession.create("kael",FIGHTERS,4);session.record_result("one",True)
    restored=ArcadeSession.from_dict(session.to_dict(),set(FIGHTERS));assert restored.position==1 and restored.opponents==session.opponents
    safe=ArcadeSession.from_dict({"fighter_id":"missing","opponents":["bad"],"seed":5},set(FIGHTERS));assert safe.fighter_id in FIGHTERS
