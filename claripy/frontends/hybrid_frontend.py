#!/usr/bin/env python

import logging
l = logging.getLogger("claripy.frontends.hybrid_frontend")

from .full_frontend import FullFrontend
from .light_frontend import LightFrontend
from .replacement_frontend import ReplacementFrontend

class HybridFrontend(FullFrontend):
    def __init__(self, solver_backend, approximation_frontend=None, **kwargs):
        FullFrontend.__init__(self, solver_backend, **kwargs)
        self._approximation_frontend = approximation_frontend if approximation_frontend is not None else ReplacementFrontend(LightFrontend(_backends['BackendVSA']))

    #
    # Storable support
    #

    def _ana_getstate(self):
        return (self._approximation_frontend, FullFrontend._ana_getstate(self))

    def _ana_setstate(self, s):
        self._approximation_frontend, full_state = s
        FullFrontend._ana_setstate(self, full_state)

    def _blank_copy(self):
        return HybridFrontend(self._solver_backend, approximation_frontend=self._approximation_frontend, cache=self._cache, timeout=self.timeout)

    #
    # Catch constraint adds and pass them to the replacement frontend
    #

    def _add_constraints(self, constraints, invalidate_cache=True):
        super(HybridFrontend, self)._add_constraints(constraints, invalidate_cache=invalidate_cache)
        self._approximation_frontend.add(constraints, invalidate_cache=invalidate_cache)

    def _cache_eval(self, e, values, n=None, exact=None, cache=None):
        super(HybridFrontend, self)._cache_eval(e, values, n=None, exact=exact, cache=cache)

        if exact is False or cache is False:
            if n > 1 and len(values) == 1:
                self._approximation_frontend.add_replacement(e, next(iter(values)))

    def _cache_max(self, e, m, exact=None, cache=None):
        super(HybridFrontend, self)._cache_max(e, m, exact=exact, cache=cache)

        if exact is False or cache is False:
            if isinstance(e, BV):
                si = BVS('limiter', e.length, max=m)
                self._approximation_frontend.add_replacement(e, e.intersection(si))

    def _cache_min(self, e, m, exact=None, cache=None):
        super(HybridFrontend, self)._cache_min(e, m, exact=exact, cache=cache)

        if exact is False or cache is False:
            if isinstance(e, BV):
                si = BVS('limiter', e.length, min=m)
                self._approximation_frontend.add_replacement(e, e.intersection(si))

    #
    # Hybrid solving
    #

    def _solve(self, extra_constraints=(), exact=None, cache=None):
        # if approximating, try the approximation backend
        if exact is False:
            try: return self._approximation_frontend.solve(extra_constraints=extra_constraints)
            except ClaripyFrontendError: pass

        # if that fails, try the exact backend
        return super(HybridFrontend, self)._solve(extra_constraints=extra_constraints, exact=exact, cache=cache)

    def _eval(self, e, n, extra_constraints=(), exact=None, cache=None):
        # if approximating, try the approximation backend
        if exact is False:
            try: return self._approximation_frontend.eval(e, n, extra_constraints=extra_constraints)
            except ClaripyFrontendError: pass

        # if that fails, try the exact backend
        return super(HybridFrontend, self)._eval(e, n, extra_constraints=extra_constraints, exact=exact, cache=cache)

    def _max(self, e, extra_constraints=(), exact=None, cache=None):
        # if approximating, try the approximation backend
        if exact is False:
            try: return self._approximation_frontend.max(e, extra_constraints=extra_constraints)
            except ClaripyFrontendError: pass

        # if that fails, try the exact backend
        return super(HybridFrontend, self)._max(e, extra_constraints=extra_constraints, exact=exact, cache=cache)

    def _min(self, e, extra_constraints=(), exact=None, cache=None):
        # if approximating, try the approximation backend
        if exact is False:
            try: return self._approximation_frontend.min(e, extra_constraints=extra_constraints)
            except ClaripyFrontendError: pass

        # if that fails, try the exact backend
        return super(HybridFrontend, self)._min(e, extra_constraints=extra_constraints, exact=exact, cache=cache)

    def _solution(self, e, v, extra_constraints=(), exact=None, cache=None):
        # if approximating, try the approximation backend
        if exact is False:
            try: return self._approximation_frontend.solution(e, v, extra_constraints=extra_constraints)
            except ClaripyFrontendError: pass

        # if that fails, try the exact backend
        return super(HybridFrontend, self)._solution(e, v, extra_constraints=extra_constraints, exact=exact, cache=cache)

    def _is_true(self, e, extra_constraints=(), exact=None, cache=None):
        # if approximating, try the approximation backend
        if exact is False:
            try: return self._approximation_frontend.is_true(e, extra_constraints=extra_constraints)
            except ClaripyFrontendError: pass

        # if that fails, try the exact backend
        return super(HybridFrontend, self)._is_true(e, extra_constraints=extra_constraints, exact=exact, cache=cache)

    def _is_false(self, e, extra_constraints=(), exact=None, cache=None):
        # if approximating, try the approximation backend
        if exact is False:
            try: return self._approximation_frontend.is_false(e, extra_constraints=extra_constraints)
            except ClaripyFrontendError: pass

        # if that fails, try the exact backend
        return super(HybridFrontend, self)._is_false(e, extra_constraints=extra_constraints, exact=exact, cache=cache)

from ..errors import ClaripyFrontendError
from .. import _backends
from ..ast.bv import BV, BVS
