# -*- coding: utf-8 -*-

import events


def AfterTransitionEventHandler(sample, event):
    """Actions to be done *after a transition* for a sample takes place
    """
    if not event.transition:
        return

    function_name = "after_{}".format(event.transition.id)
    if hasattr(events, function_name):
        # Call the after_* function from events package
        getattr(events, function_name)(sample)
