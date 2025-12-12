-- Update recently imported records based on filename
UPDATE __tablename__
  SET swe_date = to_date(
    _filedate_,
    'YYYYMMDD'
  )
  WHERE swe_date is NULL;
