/*
 * --------------------------------------------------------------------------------
 * Project:         WaterALLOC
 * Namespace:       RTI.WRMD.WaterALLOC.Class
 * Class:           SqliteHelper1
 * Description:     <DESCRIPTION>
 * Author:          anuragsrivastav@rti.org
 * Date:            January 01, 2018 - March 31, 2018
 * Note:            <NOTES>
 * Revision History:
 * Name:            Date:           Description:
 * 
 * 
 * --------------------------------------------------------------------------------
 */

using System;
using System.IO;
using System.Data;
using System.Collections.Generic;
using System.Linq;
using System.Data.SQLite;

namespace RTI.CWR.MMS_Support
{
    public class MyDBSqlite : IDisposable
    {
        public string dbFile { get; }
        private string ConnectionString { get; set; }
        private bool _version4Plus { get; set; }
        private SQLiteTransaction _sqltransaction { get; set; }
        private SQLiteConnection _sqlconnection { get; set; }


        public MyDBSqlite()
        {  
            
        }

        public MyDBSqlite(string dbfile)
        {
            //dbFile = Path.Combine(Path.GetDirectoryName(Application.ExecutablePath), dbfile);
            ConnectionString = GetSqLiteConnectionString(dbfile);
        }

        private string GetSqLiteConnectionString(string dbFileName)
        {
            SQLiteConnectionStringBuilder conn = new SQLiteConnectionStringBuilder
            {
                DataSource = dbFileName,
                Version = 3,
                FailIfMissing = true,
            };
            conn.Add("Compress", true);

            return conn.ConnectionString;
        }

       private bool IsTableExist(string tablename)
        {
            bool isexist = false;
            using (SQLiteConnection c = new SQLiteConnection(ConnectionString))
            {
                try
                {
                    c.Open();
                    string sql = "SELECT name FROM sqlite_master WHERE type = 'table'";
                    using (SQLiteCommand cmd = new SQLiteCommand(sql, c))
                    {
                        SQLiteDataReader r = cmd.ExecuteReader();
                        while (r.Read())
                        {
                            if (r[0].ToString() == tablename)
                            {
                                isexist = true;
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                   Console.WriteLine("ERROR [DATABASE]: " + ex.Message);
                }
                finally
                {
                    c.Close();
                }
            }
            return isexist;
        }
        
        public int ExecuteQuery(string sql)
        {
            ////using (SQLiteConnection c = new SQLiteConnection(ConnectionString))
            ////{
                int rowid=0;
                try
                {
                    CheckDatabaseConnection();
                    using (SQLiteCommand cmd = new SQLiteCommand(sql, _sqlconnection))
                    {
                        cmd.Transaction = _sqltransaction;
                        rowid = cmd.ExecuteNonQuery();
                        rowid = (int)_sqlconnection.LastInsertRowId;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                }
                finally
                {
                    CommitTransaction();
                }
                return rowid;
            //}
        }

        public object ExecuteScalar(string sql)
        {
            using (SQLiteConnection c = new SQLiteConnection(ConnectionString))
            {
                object m_value = null;
                try
                {
                    c.Open();
                    using (SQLiteCommand cmd = new SQLiteCommand(sql, c))
                    {
                        SQLiteDataReader r = cmd.ExecuteReader();
                        while (r.Read())
                        {
                            m_value = r[0];
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message + "\n" + ex.StackTrace.ToString());
                }
                finally
                {
                    c.Close();
                }
                return m_value;
            }
        }
      
        private void CheckDatabaseConnection()
        {
            if (_sqlconnection == null || _sqlconnection.State != ConnectionState.Open)
            {
                _sqlconnection = new SQLiteConnection(ConnectionString);
                _sqlconnection.Open();
                //custom functions definition
                _sqlconnection.BindFunction(new SQLiteFunctionAttribute("Power", 1, FunctionType.Scalar),
                    (Func<object[], object>)((object[] args) => PowerFunction((object[])args[1])),
                    null);
            }

            if (_sqltransaction == null)
            {
                _sqltransaction = _sqlconnection.BeginTransaction();
            }
            return;
        }

        object PowerFunction(object[] args)
        {
            var arg1 = (double)args[0];
            var arg2 = (double)args[1];
            return Math.Pow(arg1, arg2);
        }


        public DataTable GetTableFromDB(string sql, string tableName)
        {
            DataTable settingstable = new DataTable(tableName);

            try
            {
                CheckDatabaseConnection();
                using (SQLiteCommand cmd = new SQLiteCommand(sql, _sqlconnection))
                {
                    SQLiteDataReader r = cmd.ExecuteReader();
                    while (r.Read())
                    {
                        if (settingstable.Columns.Count == 0)
                        {
                            for (int i = 0; i < r.FieldCount; i++)
                            {
                                settingstable.Columns.Add(r.GetName(i), r.GetFieldType(i));
                            }
                        }
                        object[] rowValues = new object[r.FieldCount];
                        r.GetValues(rowValues);
                        settingstable.Rows.Add(rowValues);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("ERROR [DATABASE]: " + ex.Message);
            }
            finally
            {
                CommitTransaction();
            }

            return settingstable;
        }

        public bool UpdateTableFromDB(DataTable m_Table)
        {
            try
            {
                CheckDatabaseConnection();
                // store ts pattern values
                foreach (DataRow m_row in m_Table.Rows)
                {
                    string sql = "INSERT OR REPLACE INTO " + m_Table.TableName + " (";
                    for (int i = 0; i < m_Table.Columns.Count; i++)
                    {
                        if (i > 0) sql += " ,";
                        sql += m_Table.Columns[i].ColumnName;
                    }
                    sql += ") VALUES (";
                    for (int i = 0; i < m_Table.Columns.Count; i++)
                    {
                        if (i > 0) sql += " ,";
                        if (IsNumeric(m_Table.Columns[i]))
                        {
                            if (DBNull.Value.Equals(m_row[i]))
                            {
                                sql += "NULL";
                            }
                            else
                            {
                                sql += m_row[i].ToString();
                            }
                        }
                        else if (m_Table.Columns[i].DataType.ToString().Contains("Date"))
                        {
                            DateTime m_date = (DateTime)m_row[i];
                            sql += "'" + m_date.ToString("yyyy-MM-dd HH:MM:ss") + "'";
                        }
                        else
                        {
                            sql += "'" + m_row[i].ToString() + "'";
                        }
                    }
                    sql += ");";
                    using (SQLiteCommand cmd = new SQLiteCommand(sql, _sqlconnection))
                    {
                        cmd.Transaction = _sqltransaction;
                        cmd.ExecuteNonQuery();                        
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("ERROR [DATABASE]: " + ex.Message);
                return false;
            }
            finally
            {
                CommitTransaction();
            }
            return true;
        }

        public bool IsNumeric(DataColumn col)
        {
            if (col == null)
                return false;
            // Make this const
            var numericTypes = new[] { typeof(Byte), typeof(Decimal), typeof(Double),
        typeof(Int16), typeof(Int32), typeof(Int64), typeof(SByte),
        typeof(Single), typeof(UInt16), typeof(UInt32), typeof(UInt64)};
            return numericTypes.Contains(col.DataType);
        }

        public void CommitTransaction()
        {
            if (_sqltransaction != null && _sqltransaction.Connection != null)
            {
                _sqltransaction.Commit();
                _sqltransaction = null;
            }

            if (_sqlconnection != null && _sqlconnection.State == ConnectionState.Open)
            {
                _sqlconnection.Close();
                _sqlconnection = null;
            }
        }

        #region IDisposable Support
        private bool disposedValue = false; // To detect redundant calls

        protected virtual void Dispose(bool disposing)
        {
            if (!disposedValue)
            {
                if (disposing)
                {
                    // TODO: dispose managed state (managed objects).
                    if (_sqltransaction != null)
                    {
                        _sqlconnection.Close();
                        _sqltransaction.Dispose();
                    }
                }

                // TODO: free unmanaged resources (unmanaged objects) and override a finalizer below.
                // TODO: set large fields to null.

                disposedValue = true;
            }
        }

        // TODO: override a finalizer only if Dispose(bool disposing) above has code to free unmanaged resources.
        // ~SqliteHelper1() {
        //   // Do not change this code. Put cleanup code in Dispose(bool disposing) above.
        //   Dispose(false);
        // }

        // This code added to correctly implement the disposable pattern.
        public void Dispose()
        {
            // Do not change this code. Put cleanup code in Dispose(bool disposing) above.
            Dispose(true);
            // TODO: uncomment the following line if the finalizer is overridden above.
            // GC.SuppressFinalize(this);
        }
        #endregion

    }
}
