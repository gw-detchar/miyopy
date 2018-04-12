#
#! coding:utf-8


import numpy
from astropy.units import Quantity
from astropy import units 


class Array(Quantity):    
    """
    このArrayクラスは、numpy.ndarrayをベースにして各種データ処理に必要なメタデータを以下のパラメータに付与している。

    かなりの部分はGwpyのArrayをお手本につくった。まだライセンスの扱いについてよく知らないので、プライベートリポジトリにした。

    Parameters
    ----------
    value : array-like
        input data array
    unit : `~astropy.units.Unit`, optional
        physical unit of these data
    epoch : `~gwpy.time.LIGOTimeGPS`, `float`, `str`, optional
        GPS epoch associated with these data,
        any input parsable by `~gwpy.time.to_gps` is fine
    name : `str`, optional
        descriptive title for this array
    channel : `~gwpy.detector.Channel`, `str`, optional
        source data stream for these data
    dtype : `~numpy.dtype`, optional
        input data type
    copy : `bool`, optional, default: `False`
        choose to copy the input data to new memory
    subok : `bool`, optional, default: `True`
        allow passing of sub-classes by the array generator
    Returns
    -------
    array : `Array`
        a new array, with a view of the data, and all associated metadata
    Examples
    --------
    To create a new `Array` from a list of samples:
        >>> a = Array([1, 2, 3, 4, 5], 'm/s', name='my data')
        >>> print(a)
        Array([ 1., 2., 3., 4., 5.]
              unit: Unit("m / s"),
              name: 'my data',
              epoch: None,
              channel: None)
    """
    #: list of new attributes defined in this class
    #
    # this is used in __array_finalize__ to create new instances of this
    # object [http://docs.scipy.org/doc/numpy/user/basics.subclassing.html]
    _metadata_slots = ('name', 'epoch', 'channel')

    def __new__(cls, value, unit=None,  # Quantity attrs
                name=None, epoch=None, channel=None,  # new attrs
                dtype=None, copy=True, subok=True,  # ndarray attrs
                order=None, ndmin=0):
        """Create a new `Array`
        """
        # pick dtype from input array
        if dtype is None and isinstance(value, numpy.ndarray):
            dtype = value.dtype

        # parse unit with forgiveness
        if unit is not None:
            #unit = parse_unit(unit, parse_strict='warn')
            unit = unit

        # create new array
        new = super(Array, cls).__new__(cls, value, unit=unit, dtype=dtype,
                                        copy=False, order=order, subok=subok,
                                        ndmin=ndmin)

        # explicitly copy here to get ownership of the data,
        # see (astropy/astropy#7244)
        if copy:
            new = new.copy()

        # set new attributes
        if name is not None:
            new.name = name
        if epoch is not None:
            new.epoch = epoch
        if channel is not None:
            new.channel = channel

        return new

    # -- object creation ------------------------
    # methods here handle how these objects are created,
    # mainly to do with making sure metadata attributes get
    # properly reassigned from old to new

    def _wrap_function(self, function, *args, **kwargs):
        # if the output of the function is a scalar, return it as a Quantity
        # not whatever class this is
        out = super(Array, self)._wrap_function(function, *args, **kwargs)
        if out.ndim == 0:
            return Quantity(out.value, out.unit)
        return out

    def __quantity_subclass__(self, unit):
        # this is required to allow in-place ufunc operations to return
        # things that aren't basic quantities
        return type(self), True

    def __array_finalize__(self, obj):
        # format a new instance of this class starting from `obj`
        if obj is None:
            return

        # call Quantity.__array_finalize__ to handle the units
        super(Array, self).__array_finalize__(obj)

        # then update metadata
        if isinstance(obj, Quantity):
            self.__metadata_finalize__(obj, force=False)

    def __metadata_finalize__(self, obj, force=False):
        # apply metadata from obj to self if creating a new object
        for attr in self._metadata_slots:
            _attr = '_%s' % attr  # use private attribute (not property)
            # if attribute is unset, default it to None, then update
            # from obj if desired
            try:
                getattr(self, _attr)
            except AttributeError:
                update = True
            else:
                update = force
            if update:
                try:
                    val = getattr(obj, _attr)
                except AttributeError:
                    continue
                else:
                    if isinstance(val, Quantity):  # copy Quantities
                        setattr(self, _attr, type(val)(val))
                    else:
                        setattr(self, _attr, val)

    def __getattr__(self, attr):
        return super(Array, self).__getattribute__(attr)

    def __getitem__(self, item):
        new = super(Array, self).__getitem__(item)

        # return scalar as a Quantity
        if numpy.ndim(new) == 0:
            return Quantity(new, unit=self.unit)

        return new

    # -- display --------------------------------

    def _repr_helper(self, print_):
        if print_ is repr:
            opstr = '='
        else:
            opstr = ': '

        # get prefix and suffix
        prefix = '{}('.format(type(self).__name__)
        suffix = ')'
        if print_ is repr:
            prefix = '<{}'.format(prefix)
            suffix += '>'

        indent = ' ' * len(prefix)

        # format value
        arrstr = numpy.array2string(self.view(numpy.ndarray), separator=', ',
                                    prefix=prefix)

        # format unit
        metadata = [('unit', print_(self.unit) or 'dimensionless')]

        # format other metadata
        try:
            attrs = self._print_slots
        except AttributeError:
            attrs = self._metadata_slots
        for key in attrs:
            try:
                val = getattr(self, key)
            except (AttributeError, KeyError):
                val = None
            thisindent = indent + ' ' * (len(key) + len(opstr))
            metadata.append((
                key.lstrip('_'),
                print_(val).replace('\n', '\n{}'.format(thisindent)),
            ))
        metadata = (',\n{}'.format(indent)).join(
            '{0}{1}{2}'.format(key, opstr, value) for key, value in metadata)

        return "{0}{1}\n{2}{3}{4}".format(
            prefix, arrstr, indent, metadata, suffix)

    def __repr__(self):
        """Return a representation of this object
        This just represents each of the metadata objects appropriately
        after the core data array
        """
        return self._repr_helper(repr)

    def __str__(self):
        """Return a printable string format representation of this object
        This just prints each of the metadata objects appropriately
        after the core data array
        """
        return self._repr_helper(str)

    # -- Pickle helpers -------------------------

    def dumps(self):
        return super(Quantity, self).dumps()
    dumps.__doc__ = numpy.ndarray.dumps.__doc__

    def tostring(self, order='C'):
        return super(Quantity, self).tostring(order=order)
    tostring.__doc__ = numpy.ndarray.tostring.__doc__

    # -- new properties -------------------------

    # name
    @property
    def name(self):
        """Name for this data set
        :type: `str`
        """
        try:
            return self._name
        except AttributeError:
            self._name = None
            return self._name

    @name.setter
    def name(self, val):
        self._name = if_not_none(str, val)

    @name.deleter
    def name(self):
        try:
            del self._name
        except AttributeError:
            pass

    # epoch
    @property
    def epoch(self):
        """GPS epoch associated with these data
        :type: `~astropy.time.Time`
        """
        try:
            if self._epoch is None:
                return None
            return Time(*modf(self._epoch)[::-1], format='gps', scale='utc')
        except AttributeError:
            self._epoch = None
            return self._epoch

    @epoch.setter
    def epoch(self, epoch):
        if epoch is None:
            self._epoch = None
        else:
            self._epoch = Decimal(str(to_gps(epoch)))

    @epoch.deleter
    def epoch(self):
        try:
            del self._epoch
        except AttributeError:
            pass

    # channel
    @property
    def channel(self):
        """Instrumental channel associated with these data
        :type: `~gwpy.detector.Channel`
        """
        try:
            return self._channel
        except AttributeError:
            self._channel = None
            return self._channel

    @channel.setter
    def channel(self, chan):
        if isinstance(chan, Channel):
            self._channel = chan
        elif chan is None:
            self._channel = None
        else:
            self._channel = Channel(chan)

    @channel.deleter
    def channel(self):
        try:
            del self._channel
        except AttributeError:
            pass

    # unit - we override this to make the property less pedantic
    #        astropy won't allow you to set a unit that it doesn't
    #        recognise
    @property
    def unit(self):
        """The physical unit of these data
        :type: `~astropy.units.UnitBase`
        """
        try:
            return self._unit
        except AttributeError:
            return None

    @unit.setter
    def unit(self, unit):
        if not hasattr(self, '_unit') or self._unit is None:
            #self._unit = parse_unit(unit)
            self._unit = unit
        else:
            raise AttributeError(
                "Can't set attribute. To change the units of this %s, use the "
                ".to() instance method instead, otherwise use the "
                "override_unit() instance method to forcefully set a new unit."
                % type(self).__name__)

    @unit.deleter
    def unit(self):
        try:
            del self._unit
        except AttributeError:
            pass

    # -- array methods --------------------------

    def abs(self, axis=None, **kwargs):
        return self._wrap_function(numpy.abs, axis, **kwargs)
    abs.__doc__ = numpy.abs.__doc__

    def median(self, axis=None, **kwargs):
        return self._wrap_function(numpy.median, axis, **kwargs)
    median.__doc__ = numpy.median.__doc__

    def _to_own_unit(self, value, check_precision=True):
        if self.unit is None:
            try:
                self.unit = ''
                return super(Array, self)._to_own_unit(
                    value, check_precision=check_precision)
            finally:
                del self.unit
        else:
            return super(Array, self)._to_own_unit(
                value, check_precision=check_precision)
    _to_own_unit.__doc__ = Quantity._to_own_unit.__doc__



if __name__=='__main__':
    a = Array([1,2,3,4,5,6,7,8],unit='m',)
