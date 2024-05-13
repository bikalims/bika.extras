# -*- coding: utf-8 -*-

import events


def AfterTransitionEventHandler(sample, event):
    """Actions to be done *after a transition* for a sample takes place
    """
    if not event.transition and event.status["action"] != "receive":
        return

    if event.status["action"] == "receive":
        function_name = "after_{}".format(event.status["action"])
    else:
        function_name = "after_{}".format(event.transition.id)
    if hasattr(events, function_name):
        # Call the after_* function from events package
        getattr(events, function_name)(sample)
