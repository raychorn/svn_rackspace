<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
  <head>
    <title>${c.title}</title>
  </head>
  <body>
    <table>
        % for m_key in c.maint_vals.keys():
        <tr><td>${m_key}</td><td>${c.maint_vals.get(m_key)}</td></tr>
        % endfor
    </table>
  </body>
</html>
