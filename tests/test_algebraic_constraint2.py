from numpy import linspace, random

from lmfit import Minimizer, Parameters
from lmfit.lineshapes import gaussian, lorentzian


def test_constraints():

    def residual(pars, x, sigma=None, data=None):
        yg = gaussian(x, pars['amp_g'], pars['cen_g'], pars['wid_g'])
        yl = lorentzian(x, pars['amp_l'], pars['cen_l'], pars['wid_l'])

        model = yg + yl + pars['line_off'] + x * pars['line_slope']
        if data is None:
            return model
        if sigma is None:
            return (model - data)
        return (model - data) / sigma

    n = 201
    xmin = 0.
    xmax = 20.0
    x = linspace(xmin, xmax, n)

    data = (gaussian(x, 21, 8.1, 1.2) +
            lorentzian(x, 10, 9.6, 2.4) +
            random.normal(scale=0.23, size=n) +
            x*0.5)

    pfit = Parameters()
    pfit.add(name='amp_g', value=10)
    pfit.add(name='cen_g', value=9)
    pfit.add(name='wid_g', value=1)

    pfit.add(name='amp_tot', value=20)
    pfit.add(name='amp_l', expr='amp_tot - amp_g')
    pfit.add(name='cen_l', expr='1.5+cen_g')
    pfit.add(name='wid_l', expr='2*wid_g')

    pfit.add(name='line_slope', value=0.0)
    pfit.add(name='line_off', value=0.0)

    sigma = 0.021  # estimate of data error (for all data points)

    myfit = Minimizer(residual, pfit,
                      fcn_args=(x,), fcn_kws={'sigma': sigma, 'data': data},
                      scale_covar=True)

    myfit.prepare_fit()
    result = myfit.leastsq()

    assert(result.params['cen_l'].value == 1.5 + result.params['cen_g'].value)
    assert(result.params['amp_l'].value ==
           result.params['amp_tot'].value - result.params['amp_g'].value)
    assert(result.params['wid_l'].value == 2.0*result.params['wid_g'].value)

    # now, change fit slightly and re-run
    myfit.params['wid_l'].expr = '1.25*wid_g'
    result = myfit.leastsq()

    assert(result.params['cen_l'].value == 1.5 + result.params['cen_g'].value)
    assert(result.params['amp_l'].value ==
           result.params['amp_tot'].value - result.params['amp_g'].value)
    assert(result.params['wid_l'].value == 1.25*result.params['wid_g'].value)
