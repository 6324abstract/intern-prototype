import pytest

from cwdb import Cell, CWComplex
from cwdb.tts import (
    AspectInstance,
    EntityInstance,
    EntityType,
    GetterInstance,
    TaskTypeSystem,
)


def test_entity_aspect_getter():
    cw = CWComplex()
    tts = TaskTypeSystem.from_empty_context(cw)

    human: EntityType = tts.Entity.create_child("Human")
    alice: EntityInstance = human.create(name="Alice")
    bob: EntityInstance = human.create(name="Bob")
    carol: EntityInstance = human.create(name="Carol")

    loves: AspectInstance = tts.Aspect.create(name="Loves")
    alice.declare_aspect(loves, context=cw)  # Alice loves someone
    bob.declare_aspect(loves, context=cw)  # Bob loves someone
    assert loves in alice.aspects(context=cw)
    assert loves in bob.aspects(context=cw)

    dates: AspectInstance = tts.Aspect.create(name="Dates")
    carol.declare_aspect(dates, context=cw)
    assert dates in carol.aspects(context=cw)

    def get_love_subject_impl(arg: Cell):
        """
        Python implementation of a getter.
        Possibly provides the access to external world data (i.e. non-KB information)
        """
        if arg == alice.cell:
            return bob
        raise RuntimeError(f"Can't find love subject for {arg.label}")

    love_subject: GetterInstance = tts.Getter.create(
        name="get_love_subject",
        aspect=loves,
        impl=get_love_subject_impl,
        association_type=human,
        return_type=tts.Entity,
    )
    date_partner: GetterInstance = tts.Getter.create(
        name="get_date_partner",
        aspect=dates,
        return_type=tts.Entity,
        association_type=human,
    )  # no implementation

    assert love_subject in loves.getters(context=cw)
    assert date_partner in dates.getters(context=cw)

    # Getter returns a value
    assert alice.get(love_subject, context=cw) == bob

    # Getter query fails on entities that do not possess corresponding aspect
    # 1/2
    with pytest.raises(
        RuntimeError, match="get_date_partner_task requires possession of Dates"
    ):
        alice.get(date_partner, context=cw)
    # 2/2
    with pytest.raises(
        RuntimeError, match="get_love_subject_task requires possession of Loves"
    ):
        carol.get(love_subject, context=cw)

    # Getter might fail to accomplish the query when
    #  - no explicit knowledge in KB (see `test_getter_result_can_be_stored` below)
    #  - no implicit knowledge in KB (in a form of associated Strategy)
    #  - no external source of information (in a form of bound python getter
    #                                       implementation)
    #  - no knowledge in external sources (e.g. information is external world
    #                                      not available/accessible)

    with pytest.raises(RuntimeError):
        # We know that Carol has a partner (since she possesses `Dates` aspect)
        # KB don't have the explicit information about her partner.
        # External source of information is not provided
        carol.get(date_partner, context=cw)

    with pytest.raises(RuntimeError, match="Can't find love subject for Bob"):
        # We know that Bob loves someone (since he possesses `Loves` aspect)
        # KB don't have the explicit information about the love subject.
        # External source of information IS provided in a form of python function
        # The python function is only provided with information about Alice's love
        # subject, it fails for Bob
        bob.get(love_subject, context=cw)


def test_getter_result_can_be_stored():
    cw = CWComplex()
    tts = TaskTypeSystem.from_empty_context(cw)

    human: EntityType = tts.Entity.create_child("Human")
    alice: EntityInstance = human.create(name="Alice")
    bob: EntityInstance = human.create(name="Bob")

    loves: AspectInstance = tts.Aspect.create(name="Loves")
    alice.declare_aspect(loves, context=cw)  # Alice loves someone

    love_subject = tts.Getter.create(
        name="get_love_subject",
        aspect=loves,
        return_type=tts.Entity,
        association_type=human,
    )

    with pytest.raises(RuntimeError):
        alice.get(love_subject, context=cw)

    alice_loves_bob = alice.memoize(love_subject, bob, context=cw)
    assert alice_loves_bob in cw
    assert alice.get(love_subject, context=cw) == bob
